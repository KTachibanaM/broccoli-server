import uuid
import json
import logging
import time
import pika
from typing import Union, Dict, List, Tuple, Optional
from common.rpc import RPC_REQUEST_QUEUE


# todo: thread-safe??
class AmqpRpcClient(object):
    def __init__(self, host: str, port: int, logger: logging.Logger, callback_queue_name: str):
        # todo: properly close connection and channel
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host,
            port=port
        ))  # type: pika.BlockingConnection
        self.logger = logger
        self.callback_queue_name = callback_queue_name

        self.channel = self.connection.channel()  # type: pika.adapters.blocking_connection.BlockingChannel
        self.channel.queue_declare(queue=callback_queue_name, exclusive=True)
        self.channel.basic_consume(
            self.on_response,
            no_ack=True,
            queue=callback_queue_name
        )
        self.current_correlation_id = None,  # type: Optional[str]
        self.current_response = None  # type: Optional[Dict]

    def on_response(
        self,
        _: pika.adapters.blocking_connection.BlockingChannel,
        _1: pika.spec.Basic.Deliver,
        properties: pika.BasicProperties,
        body: str
    ):
        if self.current_correlation_id == properties.correlation_id:
            # todo: json.loads failure
            self.current_response = json.loads(body)

    def blocking_call(self, verb: str, metadata: Dict, payload: Dict) -> Tuple[bool, Union[Dict, List, str]]:
        self.current_correlation_id = str(uuid.uuid4())
        self.current_response = None

        # todo: timeout?
        self.channel.basic_publish(
            exchange='',
            routing_key=RPC_REQUEST_QUEUE,
            body=json.dumps({
                'verb': verb,
                'metadata': metadata,
                'payload': payload
            }),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json',
                reply_to=self.callback_queue_name,
                correlation_id=self.current_correlation_id
            )
        )
        self.logger.debug(f"Sent rpc request correlation_id={self.current_correlation_id} verb={verb} "
                          f"metadata={metadata} payload={payload}")

        # todo: pass in values
        trials = 100
        while trials > 0 and self.current_response is None:
            time.sleep(0.05)
            trials -= 1
            self.connection.process_data_events()
        if self.current_response is None:
            return False, f"Response timed out after {100 * 0.05} seconds"

        self.logger.debug(f"Received rpc response correlation_id={self.current_correlation_id} "
                          f"response={self.current_response}")
        response = self.current_response  # type: Dict
        if 'status' not in response or type(response['status']) != str or \
                'payload' not in response or type(response['payload']) not in [dict, list]:
            self.logger.error(f"Invalid response {response}")
            return False, 'Invalid response'

        status = response['status']  # type: str
        payload = response['payload']  # type: Union[Dict, List]
        if status not in ['ok', 'error']:
            self.logger.warning(f"Invalid status {status}")
            return False, 'Invalid status'

        if status == 'error':
            if 'message' not in payload or type(payload['message']) != str:
                return False, 'Invalid error'
            message = payload['message']
            self.logger.debug(f"Rpc error correlation_id={self.current_correlation_id} message={message}")
            return False, message

        if status == 'ok':
            self.logger.debug(f"Rpc ok correlation_id={self.current_correlation_id} payload={payload}")
            return True, payload

    def blocking_query(self, q: Dict) -> List[Dict]:
        status, message_or_payload = self.blocking_call(
            verb='query',
            metadata={},
            payload=q
        )
        if not status:
            self.raise_error(f"Error making query={q}, message {message_or_payload}")
        if type(message_or_payload) != list:
            self.raise_error(f"Payload {message_or_payload} is not a list")
        return message_or_payload

    def blocking_update_one(self, filter_q: Dict, update_doc: Dict):
        status, message = self.blocking_call(
            verb="update_one",
            metadata={},
            payload={
                "filter_q": filter_q,
                "update_doc": update_doc
            }
        )
        if not status:
            self.raise_error(f"Error making update_one filter_q={filter_q}, update_doc={update_doc}, message {message}")

    def blocking_update_one_binary_string(self, filter_q: Dict, key: str, binary_string: List[bool]):
        status, message = self.blocking_call(
            verb="update_one_binary_string",
            metadata={},
            payload={
                "filter_q": filter_q,
                "key": key,
                "binary_string": "".join(list(map(lambda b: "1" if b else "0", binary_string)))
            }
        )
        if not status:
            self.raise_error(f"Error making update_one_binary_string filter_q={filter_q} key={key} "
                             f"binary_string={binary_string}, message {message}")

    def blocking_append(self, idempotency_key: str, doc: Dict):
        status, message = self.blocking_call(
            verb="append",
            metadata={
                "idempotency_key": idempotency_key
            },
            payload=doc
        )
        if not status:
            self.raise_error(f"Error making append idempotency_key={idempotency_key} doc={doc}, message {message}")

    def raise_error(self, message: str):
        self.logger.error(message)
        raise Exception(message)
