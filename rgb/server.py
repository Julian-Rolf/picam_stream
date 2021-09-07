import io
import socket
import struct
import configparser
import numpy as np
import cv2

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
    print('established connection')
    while True:
        # Read the length of the image
        image_length = struct.unpack('<L', connection.read(4))[0]

        buffer = connection.read(image_length)

        fwidth = (WIDTH + 31) // 32 * 32
        fheight = (HEIGHT + 15) // 16 * 16
        # Load the Y (luminance) data from the stream
        Y = np.frombuffer(buffer, dtype=np.uint8, count=fwidth *
                          fheight).reshape((fheight, fwidth))
        # Load the UV (chrominance) data from the stream, and double its size
        U = np.frombuffer(buffer, dtype=np.uint8, count=(fwidth//2)*(fheight//2)
                          ).reshape((fheight//2, fwidth//2)).repeat(2, axis=0).repeat(2, axis=1)
        V = np.frombuffer(buffer, dtype=np.uint8, count=(fwidth//2)*(fheight//2)
                          ).reshape((fheight//2, fwidth//2)).repeat(2, axis=0).repeat(2, axis=1)
        # Stack the YUV channels together, crop the actual resolution, convert to
        # floating point for later calculations, and apply the standard biases
        YUV = np.dstack((Y, U, V))[:HEIGHT, :WIDTH, :].astype(np.float)
        YUV[:, :, 0] = YUV[:, :, 0] - 16   # Offset Y by 16
        YUV[:, :, 1:] = YUV[:, :, 1:] - 128  # Offset UV by 128
        # YUV conversion matrix from ITU-R BT.601 version (SDTV)
        #              Y       U       V
        M = np.array([[1.164,  0.000,  1.596],    # R
                      [1.164, -0.392, -0.813],    # G
                      [1.164,  2.017,  0.000]])   # B
        # Take the dot product with the matrix to produce RGB output, clamp the
        # results to byte range and convert to bytes
        RGB = YUV.dot(M.T).clip(0, 255).astype(np.uint8)

        cv2.imshow('image', RGB)
        cv2.waitKey(1)

finally:
    connection.close()
    server_socket.close()
