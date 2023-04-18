import socket
import struct
import cv2
import av
from mycodecs import *

decoder = CodecContextEncoder(640, 480, 30, "15")

def run():
    # set up socket
    TCP_IP = '0.0.0.0'
    TCP_PORT = 8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((TCP_IP, TCP_PORT))

    print("Waiting for connection...")
    sock.listen(1)

    # Accept connections from clients
    conn, addr = sock.accept()
    print('Connection address:', addr)
    conn.settimeout(10.0)

    while True:
        size_data = b''

        try:
            # Read size + buffer from socket.
            while len(size_data) < 4:
                data = conn.recv(4 - len(size_data))
                if len(data) == 0:
                    raise Exception()
                size_data += data

            size = struct.unpack('<L', size_data)[0]

            # Receive the encoded frame data.
            video_data = b''
            while len(video_data) < size:
                data = conn.recv(size - len(video_data))
                if len(data) == 0:
                    raise Exception()
                video_data += data
        except:
            conn.close()
            break

        img_bgr = decoder.decode_to_bgr_img(video_data)
        if img_bgr is not None:
            cv2.imshow('Server Video', img_bgr)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # release everything
    cv2.destroyAllWindows()
    sock.close()

while True:
    run()