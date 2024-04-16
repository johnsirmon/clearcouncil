import os

# the base class to inherit from when creating your own formatter.
from youtube_transcript_api.formatters import Formatter

# some provided subclasses, each outputs a different string format.
from youtube_transcript_api.formatters import JSONFormatter
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api.formatters import WebVTTFormatter
from youtube_transcript_api.formatters import SRTFormatter
from youtube_transcript_api import YouTubeTranscriptApi

# The video ID is the part of the YouTube URL after "v=" and before "&" if it's also in a playlist.
video_id = "y7wMTwJN7rA"

# Get the transcript
transcript = YouTubeTranscriptApi.get_transcript(video_id)

# The transcript is a list of dictionaries where each dictionary contains 'text', 'start', and 'duration' keys.
# You can format it as you like, here's an example of how to format it as a single string:
formatted_transcript = "\n".join([entry['text'] for entry in transcript])

# Create the directory if it doesn't exist
directory = "data/transcripts"
os.makedirs(directory, exist_ok=True)

# Write the transcript to a file
file_path = os.path.join(directory, f"{video_id}_transcript.txt")
with open(file_path, 'w') as f:
    f.write(formatted_transcript)
