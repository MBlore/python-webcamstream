import io
import av
import cv2
import numpy as np

# The best way I've found to encode/decode the video data so far.
class CodecContextEncoder:
    def __init__(self, width, height, fps, crf):
        self.width = width
        self.height = height
        self.fps = fps
        self.crf = crf
        
        # Set up the codec context for the H264 encoder/decoder.
        self.codec = av.CodecContext.create('h264', 'w')
        self.codec.width = width
        self.codec.height = height
        self.codec.bit_rate = 2000000
        self.codec.framerate = 30
        self.codec.pix_fmt = 'yuv420p'
        self.codec.options = {'tune': 'zerolatency'}

        self.decoder = av.CodecContext.create('h264', 'r')

    def encode_bgr_to_bytes(self, img_bgr: np.ndarray):
        img_yuv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YUV_I420)
        frame = av.VideoFrame.from_ndarray(img_yuv, format='yuv420p')
        encoded_packets = self.codec.encode(frame)
        if len(encoded_packets) == 0:
            return None
        
        encoded_packet_bytes = bytes(encoded_packets[0])
        return encoded_packet_bytes

    def decode_to_bgr_img(self, bytes) -> np.ndarray:
        packet = av.packet.Packet(bytes)
        decoded_video_frames = self.decoder.decode(packet)

        if len(decoded_video_frames) == 0:
            return None

        decoded_frame = decoded_video_frames[0].to_ndarray(format='yuv420p')
        frame = cv2.cvtColor(decoded_frame, cv2.COLOR_YUV2BGR_I420)

        return frame

# This was an old way of encoding the data, but it's really inefficient.
class ContainerEncoder:
    def __init__(self, width, height, fps, crf):
        self.width = width
        self.height = height
        self.crf = crf
        self.fps = fps

    def encode_bgr_to_bytes(self, img):
        # Convert to YUV.
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)

        output_memory_file = io.BytesIO()

        output = av.open(output_memory_file, 'w', format="mp4")
        stream = output.add_stream('h264', str(self.fps))
        stream.width = self.width
        stream.height = self.height
        stream.pix_fmt = 'yuv420p'
        stream.options = {'crf': self.crf, 'threads': '8'}

        frame = av.VideoFrame.from_ndarray(img_yuv, format='yuv420p')
        packet = stream.encode(frame)
        output.mux(packet)

        # Flush the encoder
        packet = stream.encode(None)
        output.mux(packet)
        output.close()

        output_memory_file.seek(0)
        video_bytes = output_memory_file.read()

        return video_bytes
    
    def decode_to_bgr_img(self, bytes):
        input_memory_file = io.BytesIO(bytes)

        # Open the video container.
        container = av.open(input_memory_file, 'r', format="mp4")

        for packet in container.demux():
            for frame in packet.decode():
                frame_bgr = cv2.cvtColor(frame.to_ndarray(format='yuv420p'), cv2.COLOR_YUV2BGR_I420)
                return frame_bgr