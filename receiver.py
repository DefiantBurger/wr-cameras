import subprocess
import requests


# get list of rtsp streams from http://127.0.0.1:9997/v3/paths/list
def get_available_streams():
	resp = requests.get("http://127.0.0.1:9997/v3/paths/list")
	resp.raise_for_status()

	# Stream name: $.items[*].name
	# Stream ready: $.items[*].ready
	streams = [item["name"] for item in resp.json()["items"] if item["ready"]]
	return streams


def receive_stream(name):
	# gst-launch-1.0 rtspsrc location=rtsp://127.0.0.1:8554/test latency=0 ! \
	# rtph264depay ! h264parse ! decodebin ! videoconvert ! autovideosink sync=false

	subprocess.Popen(
		[
			"gst-launch-1.0",
			"rtspsrc",
			f"location=rtsp://127.0.0.1:8554/{name}",
			"latency=0",
			"!",
			"rtph264depay",
			"!",
			"h264parse",
			"!",
			"decodebin",
			"!",
			"videoconvert",
			"!",
			"autovideosink",
			"sync=false",
		]
	)
	print(f"Receiver stream launched for stream {name}.")


def main():
	streams = get_available_streams()
	if not streams:
		print("No available streams found.")
		return
	for stream in streams:
		print(f"Available stream: {stream}")
		receive_stream(stream)


if __name__ == "__main__":
	main()
