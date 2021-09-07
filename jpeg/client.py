import io
import socket
import struct
import time
import picamera
import configparser

config = configparser.ConfigParser()
config.read('../config.ini')

IP = str(config['DEFAULT']['IP'])
PORT = int(config['DEFAULT']['Port'])
WIDTH = int(config['CAMERA']['Width'])
HEIGHT = int(config['CAMERA']['Height'])
FRAMERATE = int(config['CAMERA']['Framerate'])
CAPTURE_TIME = int(config['CAMERA']['Capturetime'])

client_socket = socket.socket()
client_socket.connect((IP, PORT))
connection = client_socket.makefile('wb')

try:
    with picamera.PiCamera() as camera:
        camera.resolution = (WIDTH, HEIGHT)
        camera.framerate = FRAMERATE

        # camera warmup
        time.sleep(2)
        
        start = time.time()
        stream = io.BytesIO()

        # Use the video-port for captures...
        for foo in camera.capture_continuous(stream, 'jpeg'):
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            if time.time() - start > CAPTURE_TIME:
                break
            # reset stream
            stream.seek(0)
            stream.truncate()
    # finish flag
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()


