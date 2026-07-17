.PHONY: stream

stream: streamer.py
	uv run streamer.py

receive: receiver.py
	uv run receiver.py