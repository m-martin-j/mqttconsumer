# https://github.com/eclipse/paho.mqtt.python/blob/master/examples/client_sub-class.py

from typing import Callable, List
from threading import Thread
import logging
import time
import json

import paho.mqtt.client as mqtt
import pandas as pd


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
    def __init__(
            self,
            broker_address: str,
            broker_port: int, 
            topics: dict,
            on_data_ready: Callable,
            max_connect_retries: int = 20):
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

        self._expected_n_fields = None

    def handle_message(self, msgs: List) -> None:
        """Specialization of MQTTConsumer's method.

        Args:
            msgs (List): The received messages.
        """
        
        while len(msgs) > 0:
            msg = msgs.pop(0)

            if msg.topic == self.topics['data']:
                data_msg = json.loads(msg.payload.decode(self.encoding))
                data_payload = data_msg['payload']
                timestamp = data_msg['timestamp']
                logger.debug(f'Received data with timestamp {timestamp}.')
                data_struc = self._structure_payload_data(data_payload)
                data_struc.loc[:, 'timestamp'] = [timestamp]
                # data_struc.set_index(pd.Index([timestamp]), append=False, inplace=True)
                self._on_data_ready(data_struc)

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
            data: dict) -> pd.DataFrame:
        """Structures data into pandas DataFrame format. 

        Args:
            data (dict): The data.

        Returns:
            pd.DataFrame: Data as pd.DataFrame, shape: [1 x n_fields].
        """
        self._guess_payload_data_shape(data)
        ret = pd.DataFrame().from_dict(data, orient='columns')
        logger.debug(f'Payload data shape: {len(ret.index)} x {len(ret.columns)}')
        return ret
