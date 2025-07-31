"""Example script to run the MQTT consumer. See README.md for more details."""


import os
import sys
import time
import logging

from mqttconsumer import MQTTConsumer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MQTT_BROKER_ADDRESS = os.getenv('MQTT_BROKER_ADDRESS', None)
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', 1883))
MQTT_TOPIC_EXAMPLE_1 = os.getenv('MQTT_TOPIC_EXAMPLE_1', None)


def cbck_1(message):
    print(f"cbck_1 received message: {message}")


if __name__ == '__main__':
    if MQTT_BROKER_ADDRESS and MQTT_TOPIC_EXAMPLE_1:
        logger.info(f"MQTT client configured: {MQTT_BROKER_ADDRESS}, topic: {MQTT_TOPIC_EXAMPLE_1}, port: {MQTT_BROKER_PORT}")
        mc = MQTTConsumer(
            broker_address=MQTT_BROKER_ADDRESS,
            broker_port=MQTT_BROKER_PORT)
        mc.start()  # do not subscribe to anything before connection is established

        mc.add_topic_callback(
            topic=MQTT_TOPIC_EXAMPLE_1,
            callback=cbck_1)

        mc.publish(
            topic=MQTT_TOPIC_EXAMPLE_1,
            payload='Hello from MQTT consumer example script!')

        time.sleep(1)
        mc.stop()

    else:
        logger.error("MQTT broker address, topic, or port not set. Please check your environment variables.")
        sys.exit(1)