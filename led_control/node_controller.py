#!/usr/bin/env python3
# Distributed under CC0 1.0 Universal (CC0 1.0) Public Domain Dedication.
# pylint: disable=ungrouped-imports,wrong-import-position

"""
An interface between Cyphal and artnet_controller.
"""

import os
import sys
import asyncio
import logging
import pycyphal
import pycyphal.application

import zubax.primitive.byte
import uavcan.node

import artnet_controller
import numpy as np

ARTNET_IP_ADDRESS = "192.168.1.202"


class NodeController:
    REGISTER_FILE = "node_controller_app.db"

    def __init__(self) -> None:
        node_info = uavcan.node.GetInfo_1.Response(
            software_version=uavcan.node.Version_1(major=1, minor=0),
            name="org.sveta_cyber_corp.app",
        )
        # The Node class is basically the central part of the library -- it is the bridge between the application and
        # the UAVCAN network. Also, it implements certain standard application-layer functions, such as publishing
        # heartbeats and port introspection messages, responding to GetInfo, serving the register API, etc.
        # The register file stores the configuration parameters of our node (you can inspect it using SQLite Browser).
        self._node = pycyphal.application.make_node(node_info, NodeController.REGISTER_FILE)

        # Published heartbeat fields can be configured as follows.
        self._node.heartbeat_publisher.mode = uavcan.node.Mode_1.OPERATIONAL  # type: ignore
        self._node.heartbeat_publisher.vendor_specific_status_code = os.getpid() % 100

        # Now we can create ports to interact with the network.
        # They can also be created or destroyed later at any point after initialization.
        # A port is created by specifying its data type and its name (similar to topic names in ROS or DDS).
        # The subject-ID is obtained from the standard register named "UAVCAN__SUB__LED_FRAME__ID".
        self._sub_led_fr = self._node.make_subscriber(zubax.primitive.byte.Vector8192_1, "led_frame")

        # Create ArtnetInterface
        self._artnet_interface = artnet_controller.ArtnetInterface(
            target_ip=ARTNET_IP_ADDRESS, num_bars=16, num_leds_per_bar=121
        )

        # Create another RPC-server using a standard service type for which a fixed service-ID is defined.
        # We don't specify the port name so the service-ID defaults to the fixed port-ID.
        # We could, of course, use it with a different service-ID as well, if needed.
        self._node.get_server(uavcan.node.ExecuteCommand_1).serve_in_background(self._serve_execute_command)

        self._node.start()  # Don't forget to start the node!

    @staticmethod
    async def _serve_execute_command(
        request: uavcan.node.ExecuteCommand_1.Request,
        metadata: pycyphal.presentation.ServiceRequestMetadata,
    ) -> uavcan.node.ExecuteCommand_1.Response:
        logging.info("Execute command request %s from node %d", request, metadata.client_node_id)
        if request.command == uavcan.node.ExecuteCommand_1.Request.COMMAND_FACTORY_RESET:
            try:
                os.unlink(NodeController.REGISTER_FILE)  # Reset to defaults by removing the register file.
            except OSError:  # Do nothing if already removed.
                pass
            return uavcan.node.ExecuteCommand_1.Response(uavcan.node.ExecuteCommand_1.Response.STATUS_SUCCESS)
        return uavcan.node.ExecuteCommand_1.Response(uavcan.node.ExecuteCommand_1.Response.STATUS_BAD_COMMAND)

    def _process_led_frame(self, led_frame: zubax.primitive.byte.Vector8192_1) -> None:
        logging.info("LED frame received: %s", led_frame)
        # Create a random frame
        if led_frame.value.size < (16 * 121 * 3):
            target_size = 5808
            current_size = led_frame.value.size
            pad_size = target_size - current_size
            new_frame = np.pad(led_frame.value, (0, pad_size), "constant")
        if led_frame.value.size > (16 * 121 * 3):
            new_frame = led_frame.value[: 16 * 121 * 3]
        reshaped_led_frame = np.reshape(new_frame, (16, 121, 3))
        self._artnet_interface.set_frame(reshaped_led_frame)
        self._artnet_interface.show()

    async def run(self) -> None:
        """
        The main method that runs the business logic. It is also possible to use the library in an IoC-style
        by using receive_in_background() for all subscriptions if desired.
        """
        logging.info("Application started")
        print("Running. Press Ctrl+C to stop.", file=sys.stderr)

        # This loop wil exit automatically when the node is close()d. It is also possible to use receive() instead.
        async for m, _metadata in self._sub_led_fr:
            assert isinstance(m, zubax.primitive.byte.Vector8192_1)
            self._process_led_frame(m)

    def close(self) -> None:
        """
        This will close all the underlying resources down to the transport interface and all publishers/servers/etc.
        All pending tasks such as serve_in_background()/receive_in_background() will notice this and exit automatically.
        """
        self._node.close()


async def main() -> None:
    logging.root.setLevel(logging.INFO)
    app = NodeController()
    try:
        await app.run()
    except KeyboardInterrupt:
        pass
    finally:
        app.close()


if __name__ == "__main__":
    asyncio.run(main())
