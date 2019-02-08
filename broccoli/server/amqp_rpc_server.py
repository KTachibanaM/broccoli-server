import json
import pika
import logging
from typing import Union, Dict, List
from server.rpc_core import RpcCore


class ResponseMetadata(object):
    def __init__(self, reply_to_queue: str, correlation_id: str, delivery_tag):
        self.reply_to_queue = reply_to_queue
        self.correlation_id = correlation_id
        self.delivery_tag = delivery_tag

    def __str__(self):
        return f"reply_to_queue={self.reply_to_queue} correlation_id={self.correlation_id} " \
            f"delivery_tag={self.delivery_tag}"


class AmqpRpcServer(object):
    def __init__(self, host: str, port: int, rpc_request_queue_name: str, rpc_core: RpcCore, logger: logging.Logger):
        # todo: properly close the connection and channel
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
        self.channel = self.connection.channel()  # type: pika.adapters.blocking_connection.BlockingChannel
        self.channel.queue_declare(queue=rpc_request_queue_name)
        self.rpc_request_queue_name = rpc_request_queue_name
        self.rpc_core = rpc_core
        self.logger = logger

    def start_block_consuming(self):
        self.logger.info("Start consuming messages")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=self.rpc_request_queue_name)
        self.channel.start_consuming()

    def on_request(
            self,
            _: pika.adapters.blocking_connection.BlockingChannel,
            method: pika.spec.Basic.Deliver,
            properties: pika.BasicProperties,
            body: str
    ):
        r_metadata = ResponseMetadata(
            reply_to_queue=properties.reply_to,
            correlation_id=properties.correlation_id,
            delivery_tag=method.delivery_tag)

        # todo: json parse failure
        parsed_body = json.loads(body)
        status, result_or_message = self.rpc_core.call(parsed_body)
        if not status:
            self.respond_error(r_metadata, result_or_message)
        elif result_or_message is None or result_or_message == '':
            self.respond_ok(r_metadata, {})
        else:
            self.respond_ok(r_metadata, result_or_message)

    def respond_ok(self, r_metadata: ResponseMetadata, payload: Union[List[Dict], Dict]):
        self.respond(r_metadata, 'ok', payload)

    def respond_error(self, r_metadata: ResponseMetadata, message: str):
        self.respond(r_metadata, 'error', {'message': message})

    def respond(self, r_metadata: ResponseMetadata, status: str, payload: Dict):
        self.channel.basic_publish(
            exchange='',
            routing_key=r_metadata.reply_to_queue,
            body=json.dumps({
                'status': status,
                'payload': payload
            }),
            properties=pika.BasicProperties(
                correlation_id=r_metadata.correlation_id,
                content_type='application/json'
            )
        )
        self.channel.basic_ack(delivery_tag=r_metadata.delivery_tag)
        self.logger.debug(f"Sent rpc response r_metadata={r_metadata} status={status} payload={payload}")
