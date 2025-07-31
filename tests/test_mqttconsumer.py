
import time
import logging
import unittest
import random

import tests.config as config
from mqttconsumer.mqtt_consumer import MQTTConsumer

logger = logging.getLogger(__name__)


class TestMqttConsumer(unittest.TestCase):
    """Tests for `mqttconsumer` package."""

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

        self.random_topic = f"test/topic/{random.randint(100000000, 999999999)}"
        logger.info(f"Using random topic: {self.random_topic}")
        self.consumer = MQTTConsumer(
            broker_address=config.MQTT_BROKER_ADDRESS,
            broker_port=config.MQTT_BROKER_PORT)

    def tearDown(self):
        self.consumer.stop()

    def test_publish(self):
        test_message = "Test message"
        self.received_message = None

        def on_message_received(message):
            logger.info(f"Message received: {message}")
            self.received_message = message

        self.consumer.start()
        self.assertTrue(self.consumer.is_connected)

        self.consumer.add_topic_callback(
            topic=self.random_topic,
            callback=on_message_received)

        self.consumer.publish(
            topic=self.random_topic,
            payload=test_message)

        retries = 5
        while self.received_message is None and retries > 0:
            time.sleep(1)
            retries -= 1
        self.assertEqual(self.received_message, test_message)
