import collections
import cv2
import numpy as np
import signal
import sys
import threading
import time
import yaml


class programBreaker:
  break_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.break_program)
    signal.signal(signal.SIGTERM, self.break_program)

  def break_program(self, signum, _stack_frame):
    self.break_now = True


class argusStream:
    def __init__(self, src):
        try:
            self.capture = cv2.VideoCapture(src, cv2.CAP_GSTREAMER)
            self.thread = threading.Thread(target=self.update, args=(), daemon=True)
            self.thread.start()
        except :
            breaker.break_program

    def update(self):
        while self.capture.isOpened():
            try:
                _, self._frame = self.capture.read()
            except:
                sys.exit()

    @property
    def frame(self):
        return self._frame


def gstreamer_pipeline(
    camera_id=0,
    frame_size=[960, 540],
    msg_frame_size = [960, 540],
    framerate=30,
    flip_method=0,
):
    capture_width, capture_height = frame_size
    display_width, display_height = msg_frame_size

    return (
        f"nvarguscamerasrc sensor-id={camera_id} do-timestamp=true ! \
        queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 max-size-bytes=65536 ! \
        video/x-raw(memory:NVMM), width=(int){capture_width}, height=(int){capture_height}, \
        format=(string)NV12, framerate=(fraction){framerate}/1 ! \
        nvvidconv flip-method={flip_method} ! \
        video/x-raw,  format=(string)BGRx, width=(int){display_width}, height=(int){display_height} ! \
        videoconvert ! \
        appsink sync=false max-buffers=1 drop=True"
    )


with open('./camera.param.yaml') as f:
    cameras = yaml.load(f)


CameraConfig = collections.namedtuple('Camera', ['name', 'src', 'frame_size', 'msg_frame_size'])
Stream = collections.namedtuple('Stream', ['name', 'stream', 'camera_config'])
streams_list = []

for camera in cameras:
    camera_config = CameraConfig(**camera["camera"])
    stream_string = gstreamer_pipeline(
        camera_id=camera_config.src,
        frame_size=camera_config.frame_size,
        msg_frame_size=camera_config.msg_frame_size, 
        )
    stream = Stream(camera_config.name, argusStream(stream_string), camera_config)
    streams_list.append(stream)

breaker = programBreaker()

while not breaker.break_now:
    
    for camera_stream in streams_list:
        try:
            frame = camera_stream.stream.frame
            frame = cv2.resize(frame, (320, 240))
            cv2.imshow(camera_stream.name, frame)

        except Exception as e:
            continue

    if cv2.waitKey(1) == ord('q'):
        break

for camera_stream in streams_list:
    camera_stream.stream.capture.release()

cv2.destroyAllWindows()
