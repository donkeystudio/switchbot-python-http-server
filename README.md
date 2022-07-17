# switchbot-python-http-server
HTTP Server to receive BLE commands to control Switch Bot devices.

## Usage
This program aims to provide a better solution to control Switch Bot devices when integrating with Homebridge. The current official Switch Bot plugins on Homebridge does not provide a stable BLE connection to the SwitchBot devices, especially when running on a RaspberryPi. Users who use this program can consider to install [homebridge-http-switch](https://github.com/Supereg/homebridge-http-switch) plugin to use with this program.

## Dependencies
```
apt-get -y update
apt-get -y install bluetooth bluez
python3 -m pip install -r requirements.txt
```
If `pip` is not found. Refer to [here](https://pip.pypa.io/en/stable/installation/).

## [Docker](https://hub.docker.com/r/donkeystudio/switchbot-python-http-server)
Supported architectures: `linux/arm/v7`, `linux/arm64`, `linux/amd64`
```
docker run --rm --network=host -v /var/run/dbus:/var/run/dbus donkeystudio/switchbot-python-http-server 
```

## Startup Configuration
```
python3 main.py --help
```

```
usage: main.py [-h] [-u USER] [-pwd PASSWORD] [-p PORT] [-on ON_OR_OK] [-off OFF_OR_FAIL]

optional arguments:
  -h,               --help                      show this help message and exit
  -u USER,          --user USER                 Username (default: None)
  -pwd PASSWORD,    --password PASSWORD         Password (default: None)
  -p PORT,          --port PORT                 Port (default: 8080)
  -on ON_OR_OK,     --on_or_ok ON_OR_OK         Value to return if device is On or the requested action was executed successfully (default: 1)
  -off OFF_OR_FAIL, --off_or_fail OFF_OR_FAIL   Value to return if device is Off or the requested action was failed to execute (default: 0)
```
## API
### Authorization
Basic HTTP Authorization is supported. Username and password are setup using `-u/--user` and `-pwd / --password` arguments

```http
GET /?command=XXX&device=XX:XX:XX:XX:XX&interface=0&connect_timeout=5
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `command` | `string` | **Required**. Command to Switchbot device. Support the following: <br/>1. `on`: Switch mode - Turn on <br/>2. `off`: Switch mode - Turn off<br/>3. `press`: Press mode - Press<br/>4. `status`: Status of the device |
| `device` | `string` | **Required**. BLE MAC address of the Switchbot device. Can be either XX:XX:XX or XX-XX-XX formats |
| `interface` | `number` | _Optional_. ID of the HCI bluetooth interface. _Default `0` for `hci0` interface_ |
| `connect_timeout` | `number` | _Optional_. Set connect timeout before stopping the request. _Default `5` seconds_ |

Return: `1` for successful request or the device status is ON; `0` for otherwise. Response codes can be changed by setting `-on / --on_or_ok` and `-off / --off_or_fail` arguments
