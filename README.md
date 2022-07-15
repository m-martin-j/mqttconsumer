# MQTT Consumer
Code for using MQTT in analytics-related applications.

## Installation

### Dependencies
* Python >= 3.9.*
* Poetry >= 1.1.13

### Via Poetry
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

### As Package
Instructions on how to add this code as released Python package, hosted in this GitLab can be found in
[Confluence](https://confluence.fzi.de/display/Project194/Python+Package+Workflows).

