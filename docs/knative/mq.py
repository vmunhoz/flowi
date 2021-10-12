import pika

host = "10.152.183.2"
credentials = pika.PlainCredentials("default_user_4K827kKEBuhg1g9eOEF", "EKBEpra_Mp3l44S8A7R0rE90oTYQK_Lo")
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue="hello")
channel.basic_publish(exchange="", routing_key="hello", body="Hello World!")
print(" [x] Sent 'Hello World!'")


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(queue="hello", auto_ack=True, on_message_callback=callback)
print(" [*] Waiting for messages. To exit press CTRL+C")
channel.start_consuming()

connection.close()
