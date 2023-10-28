import os
import requests
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi

# Function to download a video from YouTube
def download_video(video_url, output_path):
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    stream.download(output_path)
    return yt.title

# Function to download closed captions for a video
def download_captions(video_url):
    video_id = video_url.split("v=")[1]
    try:
        transcripts = YouTubeTranscriptApi.get_transcripts([video_id], languages=["en"])
        if transcripts:
            with open(os.path.join(output_folder, f"{video_title}_captions.xml"), 'w+', encoding='utf-8') as f:
                f.write(str(transcripts[0]))
            return "Captions downloaded successfully."
        else:
            return "No captions available for this video."
    except Exception as e:
        return f"Failed to download captions: {str(e)}"

# Usage example
if __name__ == "__main__":
    video_urls = ["https://www.youtube.com/watch?v=qrvK_KuIeJk&list=PLI1yx5Z0Lrv77D_g1tvF9u3FVqnrNbCRL&index=5",]
    for video_url in video_urls:
        output_folder = "output"
        video_title = download_video(video_url, output_folder)
        result = download_captions(video_url)
        print(result)
