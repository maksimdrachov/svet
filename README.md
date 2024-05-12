# sveta: zubax office lighting API

## Setup

### Server

For the whole network, one computer needs to be responsible for receiving Cyphal messages, processing them and consequently sending ArtNet packages to the Led Controller.

```bash
rm -rf ~/.pycyphal
git clone git@github.com:OpenCyphal/public_regulated_data_types.git
git clone git@github.com:Zubax/zubax_dsdl.git
export CYPHAL_PATH="$HOME/public_regulated_data_types:$HOME/zubax_dsdl"
git clone git@github.com:maksimdrachov/sveta.git
cd ~/sveta/light_server
source env.sh &
```

The last command starts up a process called `SvetaLightServer` which is responsible for receiving the Cyphal messages and subsequently controlling the LED controller (using Artnet).

### Client

Each client can use `sveta` using his own particular config which will determine which pattern gets shown in case of success/failure.

By default this config looks as follows:

```json
{
    "warning": {
        "color": "red",
        "pattern": "fade_in_out",
        "ledBars": "all" // or 0-15
    },
    "success": {
        "color": "green",
        "pattern": "static",
        "ledBars": "all"
    }
}
```

All possible patterns can be found in `sveta/patterns`.

Each repository can have it's own particular setup, as `sveta` will look for `.sveta/settings.json` first in the current working directory; if not found it resorts to the user's home directory.

```bash
rm -rf ~/.pycyphal
export CYPHAL_PATH="$HOME/public_regulated_data_types:$HOME/zubax_dsdl"
cd ~/sveta/light_client
source env.sh &
```

To use:

```bash
sveta sleep 10 # will turn the LEDs to "success"
sveta lkdfs # non-existant command will turn the LEDs to "failure"
```
