export UAVCAN__NODE__ID=44                           # Set the local node-ID 44 (anonymous by default)
export UAVCAN__UDP__IFACE=127.0.0.1                  # Use Cyphal/UDP transport via localhost
export UAVCAN__PUB__LED_FRAME__ID=1313               # Subject "heater_voltage"          on ID 1313

export UAVCAN__DIAGNOSTIC__SEVERITY=2                # This is optional to enable logging via Cyphal

python light_controller.py                            # Run the application!
