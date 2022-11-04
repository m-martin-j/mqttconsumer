"""
Core code based on https://github.com/eclipse/paho.mqtt.python/blob/master/examples/client_sub-class.py
"""

from typing import Callable, List
from threading import Thread
import logging
import time
import json

import paho.mqtt.client as mqtt


logger = logging.getLogger(__name__)


class MQTTConsumer(mqtt.Client):

    encoding = 'utf-8'
    msgs = []

    def __init__(
            self,
            broker_address: str,
            broker_port: int,
            topics: dict,
            max_connect_retries: int =20):
        super().__init__()
        self._broker_address = broker_address
        self._broker_port = broker_port
        self._connected = False
        self._max_connect_retries = max_connect_retries

        self.topics = topics
        self.msgs = []

    def on_connect(self, mqttc, obj, flags, rc):
        self._connected = True
        # print('rc: ' + str(rc))

    def on_connect_fail(self, mqttc, obj):
        print('Connect failed')

    def on_message(self, mqttc, obj, msg):
        # print(msg.topic+' '+str(msg.qos)+' '+str(msg.payload))
        self.msgs.append(msg)

    def on_publish(self, mqttc, obj, mid):
        # print('mid: ' + str(mid))
        pass

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        # print('Subscribed: ' + str(mid) + ' ' + str(granted_qos))
        pass

    def on_log(self, mqttc, obj, level, string):
        # print(string)
        pass

    def handle_message(self, msgs):
        raise NotImplementedError()

    def init_connection(self):
        self.connect(self._broker_address, self._broker_port, self._keepalive)

        while not self._connected:
            time.sleep(0.5)
            self.loop()

        for t in list(self.topics.values()):
            self.subscribe(t, 0)

    def run(self):
        self.init_connection()

        rc = 0
        while rc == 0:
            rc = self.loop()
            if rc != 0:
                print('Lost connection!')
            self.handle_message(self.msgs)
            self.msgs = []
        return rc


class MQTTDataConsumer(MQTTConsumer, Thread):
    TOPIC_KEY_DATA = 'data'

    def __init__(
            self,
            broker_address: str,
            broker_port: int,
            topics: dict,
            on_data_ready: Callable,
            max_connect_retries: int = 20,
            data_payload_field: str ='payload',
            data_timestamp_field: str ='timestamp',
            timestamp_key: str ='timestamp'):
        """Instantiates an MQTTDataConsumer object.

        Args:
            broker_address (str): The broker's adress.
            broker_port (int): The broker's port.
            topics (dict): The topics to subscribe to, structured in a dict. Each dict key
                references one topic string. Necessary keys: 'data'
            on_data_ready (Callable): Function to call when data is ready to be provided.
                Must accept on argument: The data (one-row pandas.DataFrame with one
                column per field and a timestamp column).
            max_connect_retries (int, optional): The maximum number of reconnection
                attempts. Defaults to 20.
            data_payload_field (str, optional): The field in the received message containing the data
                payload. Defaults to 'payload'.
            data_timestamp_field (str, optional): The field in the received message containing the
                timestamp. Defaults to 'timestamp'.
            timestamp_key (str, optional): The key used for the timestamp in returned data.
                Defaults to 'timestamp'.
        """
        expected_topic_keys = ['data']
        if not set(expected_topic_keys).issubset(topics.keys()):
            raise ValueError('Provided topics does not contain all expected keys: '
                             f'{expected_topic_keys}')
        super().__init__(broker_address, broker_port, topics, max_connect_retries)
        Thread.__init__(self)
        self.init_connection()
        self.start()  # call MQTTConsumer's run in a separate thread

        self._on_data_ready = on_data_ready

        self.data_payload_field = data_payload_field
        self.data_timestamp_field = data_timestamp_field
        self.timestamp_key = timestamp_key

        self._expected_n_fields = None

    def handle_message(self, msgs: List) -> None:
        """Specialization of MQTTConsumer's method.

        Args:
            msgs (List): The received messages.
        """

        while len(msgs) > 0:
            msg = msgs.pop(0)

            if msg.topic == self.topics[self.TOPIC_KEY_DATA]:
                data_msg = json.loads(msg.payload.decode(self.encoding))
                timestamp = self._get_timestamp(data_msg)
                logger.info(f'Received data with timestamp {timestamp}.')
                data_payload = self._get_payload_data(data_msg)
                data_struc = self._structure_payload_data(data_payload, timestamp)
                self._on_data_ready(data_struc)

    def _get_payload_data(self, data_msg):
        try:
            ret = data_msg[self.data_payload_field]
            logger.debug(f'Number of fields in payload: {len(ret.keys())}')
            return ret
        except KeyError:
            raise ValueError(f'Cannot access data payload via field {self.data_payload_field}')

    def _get_timestamp(self, data_msg, unknown_val='unknown'):
        try:
            return data_msg[self.data_timestamp_field]
        except KeyError:
            logger.warning(f'Cannot access data timestamp via field {self.data_timestamp_field}')
            return unknown_val

    def _guess_payload_data_shape(
            self,
            data: dict) -> None:
        n_fields = len(data.keys())
        if self._expected_n_fields is None:
            self._expected_n_fields = n_fields
        else:
            if self._expected_n_fields != n_fields:
                logger.warning(f'Expected {self._expected_n_fields} fields in data but got '
                               f'{n_fields}')

    def _structure_payload_data(
            self,
            data: dict,
            timestamp: int) -> dict:
        """Probes and structures data. TODO

        Args:
            data (dict): The data.

        Returns:
            dict: The structured data.
        """
        self._guess_payload_data_shape(data)

        data[self.timestamp_key] = [timestamp]
        # TODO: further structuring?

        return data
