import io
import socket
import struct
from PIL import Image
import configparser
import cv2

config = configparser.ConfigParser()
config.read('../config.ini')

IP = int(config['DEFAULT']['IP'])
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
        # Read the length of the image 
        data = struct.unpack('<I', connection.read(WIDTH * HEIGHT * 3))

        # TODO: inspect data

finally:
    connection.close()
    server_socket.close()