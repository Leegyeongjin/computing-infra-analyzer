import json
import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import logging

logging.basicConfig(filename="infrastructure-magnifier.log",
                    level=logging.INFO)

# MQTT client
client = mqtt.Client()

# Flask Web Framework
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"

# Read MQTT borker information from config.json file
with open("config.json") as config_file:
    config = json.load(config_file)

broker_ip = config["mqtt"]["broker_ip"]
broker_port = config["mqtt"]["broker_port"]


# WebSocket
socketio = SocketIO(app)

topic = "info/infra/#"
topic1 = "request/infra-info/host/os"
port = 1883


# MQTT callback function for connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("connected OK")
        client.subscribe(topic)

    else:
        logging.info("conneted Fail", rc)


# MQTT callback function for disconnection
def on_disconnect(client, userdata, flags, rc=0):
    logging.info(str(rc))


# MQTT callback function for subscription
def on_subscribe(client, userdata, mid, granted_qos):
    logging.debug("subscribed: " + str(mid) + " " + str(granted_qos))


# MQTT callback function for receiving a message
def on_message(client, userdata, msg):
    received_topic = str(msg.topic)
    received_message = msg.payload.decode("utf-8")

    logging.info("received_topic: " + received_topic)
    logging.debug("received_message: " + received_message)

    to_client = dict()
    to_client["message"] = received_message
    to_client["type"] = "normal"
    # Send a message to the browser
    # (in here, 'message' is an event, and the to_client object is a message)
    socketio.emit("message", to_client)


# Assign the callback functions to its client
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message


# Flask Web Framework
# Render the index.html page when a user enters the web site
@app.route("/")
def index():
    return render_template("index.html")


# WebSocket
# Handler that operates when a client connects
@socketio.on("connect")
def handle_connect(auth):
    emit("my response", {"data": "Connected"})


# Handler that operates when a client disconnects
@socketio.on("disconnect")
def handle_disconnect():
    emit("my response", {"data": "Disconnected"})


# Handler that operates when a client's message receives
@socketio.on("message")
def handle_message(message):
    logging.debug("message: " + message)

    topic = message
    msg = "currently not used"
    if topic != "":
        client.publish(topic, "")
        logging.debug("published: " + topic + " " + msg)
    else:
        logging.debug("topic is empty")


# Main function
if __name__ == "__main__":
    client.connect(broker_ip, broker_port)
    client.loop_start()

    socketio.run(app, host="0.0.0.0", debug=True, port=5000)
