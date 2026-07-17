import os
import time

import docker
import signal
import atexit
import subprocess


class MediaMTXContainer:
	def __init__(self):
		self.client = docker.from_env()
		self.container = None

	def start_container(self):
		self.container = self.client.containers.run(
			"bluenviron/mediamtx",
			detach=True,
			network_mode="host",
			environment={"MTX_API": "yes"},
		)
		atexit.register(self.handle_exit)
		signal.signal(signal.SIGINT, self.handle_exit)
		signal.signal(signal.SIGTERM, self.handle_exit)
		print("Container started.")

	def stop_container(self):
		if self.container:
			self.container.stop()
			print("Container stopped.")
		else:
			print("No container is running.")

	def handle_exit(self, signum=None, frame=None):
		print("Signal received. Stopping container...")
		self.stop_container()
		exit(0)


def launch_camera(video_id):
	# gst-launch-1.0 v4l2src device=/dev/video0 ! \
	# image/jpeg, width=1280, height=720, framerate=30/1 ! \
	# jpegdec ! videoconvert ! \
	# x264enc tune=zerolatency bitrate=1500 speed-preset=ultrafast key-int-max=30 ! \
	# h264parse ! \
	# rtspclientsink location=rtsp://127.0.0.1:8554/test

	subprocess.Popen(
		[
			"gst-launch-1.0",
			"v4l2src",
			f"device=/dev/video{video_id}",
			"!",
			"image/jpeg, width=1280, height=720, framerate=30/1",
			"!",
			"jpegdec",
			"!",
			"videoconvert",
			"!",
			"x264enc",
			"tune=zerolatency",
			"bitrate=1500",
			"speed-preset=ultrafast",
			"key-int-max=30",
			"!",
			"h264parse",
			"!",
			"rtspclientsink",
			f"location=rtsp://127.0.0.1:8554/stream{video_id}",
		]
	)
	print(f"Camera stream launched for video ID {video_id}.")


def main():
	media_mtx = MediaMTXContainer()
	media_mtx.start_container()
	time.sleep(5)  # Wait for the container to be fully up and running

	launch_camera(video_id=0)

	while True:
		time.sleep(1)


if __name__ == "__main__":
	main()
