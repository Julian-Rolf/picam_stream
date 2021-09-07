import io
import socket
import struct
from PIL import Image
import configparser
import cv2
import numpy as np

config = configparser.ConfigParser()
config.read('../config.ini')

IP = str(config['DEFAULT']['IP'])
PORT = int(config['DEFAULT']['Port'])
WIDTH = int(config['CAMERA']['Width'])
HEIGHT = int(config['CAMERA']['Height'])

server_socket = socket.socket()
server_socket.bind((IP, PORT))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')
try:
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = Image.open(image_stream)
        
        cv2.imshow('image', np.array(image))
        cv2.waitKey(1)

finally:
    connection.close()
    server_socket.close()
