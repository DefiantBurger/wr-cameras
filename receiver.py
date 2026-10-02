import subprocess
import requests

# Streamer machine's LAN IP in production. For same-machine dev, use the
# container IP printed by streamer.py (not 127.0.0.1, docker-proxy breaks UDP).
HOST = "127.0.0.1"
PROTOCOLS = "udp"  # use "tcp" if you must read via 127.0.0.1 in dev


def get_available_streams(ip):
	resp = requests.get(f"http://{ip}:9997/v3/paths/list", timeout=5)
	resp.raise_for_status()
	return [item["name"] for item in resp.json()["items"] if item["ready"]]


def receive_stream(ip, name):
	return subprocess.Popen(
		[
			"gst-launch-1.0",
			"rtspsrc",
			f"location=rtsp://{ip}:8554/{name}",
			f"protocols={PROTOCOLS}",
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


def main():
	streams = get_available_streams(HOST)
	if not streams:
		print("No available streams found.")
		return

	procs = []
	for stream in streams:
		print(f"Receiving stream: {stream}")
		procs.append(receive_stream(HOST, stream))

	try:
		for p in procs:
			p.wait()
	except KeyboardInterrupt:
		for p in procs:
			p.terminate()


if __name__ == "__main__":
	main()