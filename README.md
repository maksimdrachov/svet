# sveta: zubax office lighting API

## Setup

```bash
rm -rf ~/.pycyphal
export CYPHAL_PATH="$HOME/public_regulated_data_types:$HOME/zubax_dsdl"
cd sveta/led_control
source my_env.sh &
```

To control the lights using Yakut:

```bash
yakut pub --count=10 1313:zubax.primitive.byte.Vector8192 "[255, 255, ..., 255]"
```

To turn on the lights using Python script:

```bash
export CYPHAL_PATH="$HOME/public_regulated_data_types:$HOME/zubax_dsdl"
cd sveta/light_control
source my_env.sh
```
