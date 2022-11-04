# MQTT Consumer
Code for using MQTT in analytics-related applications.
Based on [Eclipse Paho™ MQTT Python Client](https://github.com/eclipse/paho.mqtt.python).

## Installation

### Dependencies
* Python ^3.7

### Setup
Using pip, execute the following
```sh
pip install mqttconsumer
```

## Development

### Dependencies
* Python ^3.7
* Poetry >= 1.1.13

### Setup
(Documentation: [Python-Poetry](https://python-poetry.org/))
* install poetry
    ```sh
    python -m install poetry  # or using e.g. conda
    ```
* clone this repository
* set up virtual environment and install dependencies
    ```sh
    cd <repository_name>
    # set required python version if not using system-default (see dependencies):
    python -m poetry env use "absolute/path/to/python.exe"
    python -m poetry install  # includes dev dependencies
    ```

## To Do
* Provide usage example

## License
Code is released under the [MIT License](LICENSE).
All dependencies are copyright to the respective authors and released under the respective licenses listed in [LICENSE_LIBRARIES](LICENSE_LIBRARIES).
