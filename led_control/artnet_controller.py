#!/usr/bin/env python3
# Copyright (C) Zubax Robotics <info@zubax.com>

import numpy as np
from stupidArtnet import StupidArtnet
from typing import List

"""
An interface between numpy arrays (that contain LED data) and the StupidArtnet library.
"""

ARTNET_IP_ADDRESS = "192.168.1.202"

IP = str
RGB = tuple[int, int, int]
Frame = np.ndarray


class ArtnetInterface:
    def __init__(self, target_ip: IP, num_bars: int, num_leds_per_bar: int) -> None:
        self._num_bars = num_bars
        self._num_leds_per_bar = num_leds_per_bar
        self._leds_matrix = np.zeros((num_bars, num_leds_per_bar, 3), dtype=np.uint8)
        self._universes = ArtnetInterface.create_universes(
            target_ip=target_ip, num_leds_per_universe=num_leds_per_bar, num_universes=num_bars
        )

    @property
    def num_bars(self) -> int:
        return self._num_bars

    @property
    def num_leds_per_bar(self) -> int:
        return self._num_leds_per_bar

    def set_color(self, color: RGB) -> None:
        self._leds_matrix[:, :, :] = color
        packet_size = 3 * self.num_leds_per_bar
        packet = bytearray(packet_size)
        for i in range(packet_size):
            packet[i] = color[0]
        for universe in self._universes:
            universe.set(packet)

    def set_frame(self, frame: Frame) -> None:
        assert frame.shape == (self.num_bars, self.num_leds_per_bar, 3)
        packet_size = 3 * self.num_leds_per_bar
        for universe, bar in zip(self._universes, frame):
            packet = bytearray(packet_size)
            for i in range(self.num_leds_per_bar):
                packet[3 * i + 0] = bar[i, 0]
                packet[3 * i + 1] = bar[i, 1]
                packet[3 * i + 2] = bar[i, 2]
            universe.set(packet)

    def show(self) -> None:
        for universe in self._universes:
            universe.show()

    @staticmethod
    def create_universes(target_ip: IP, num_universes: int, num_leds_per_universe: int) -> List[StupidArtnet]:
        return [
            StupidArtnet(target_ip, universe, num_leds_per_universe * 3, 30, False, True)
            for universe in range(num_universes)
        ]


if __name__ == "__main__":
    interface = ArtnetInterface(target_ip=ARTNET_IP_ADDRESS, num_bars=16, num_leds_per_bar=121)
    # Create a white frame
    frame_white = np.full((16, 121, 3), 255, dtype=np.uint8)
    # Create a red frame
    frame_red = np.full((16, 121, 3), (255, 0, 0), dtype=np.uint8)
    # Create a green frame
    frame_green = np.full((16, 121, 3), (0, 255, 0), dtype=np.uint8)
    interface.set_frame(frame_green)
    interface.show()
