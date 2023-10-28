import os
import requests
from pytube import Playlist
from youtube_transcript_api import YouTubeTranscriptApi


# Function to download a video from YouTube
def download_video(video_url, output_path):
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    stream.download(output_path)
    return yt.title

# Function to download closed captions for a video
def download_captions(video_url, output_path):
    video_id = video_url.split("v=")[1]
    try:
        transcripts = YouTubeTranscriptApi.get_transcripts([video_id], languages=["en"])
        if transcripts:
            with open(os.path.join(output_folder, f"{video_id}_captions.xml"), 'w', encoding='utf-8') as f:
                f.write(str(transcripts[0]))
            return "Captions downloaded successfully."
        else:
            return "No captions available for this video."
    except Exception as e:
        return f"Failed to download captions: {str(e)}"

# Function to download the first 10 videos and their captions from a playlist
def download_playlist(playlist_url, output_folder, max_videos=10):
    playlist = Playlist(playlist_url)
    playlist.populate_video_urls()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, video_url in enumerate(playlist.video_urls[:max_videos]):
        video_title = download_video(video_url, output_folder)
        captions_output_path = os.path.join(output_folder, f"{video_title}_captions.xml")
        result = download_captions(video_url, captions_output_path)
        print(f"Video {i + 1}: {video_title} - {result}")

if __name__ == "__main__":
    playlist_url = "https://www.youtube.com/playlist?list=PLI1yx5Z0Lrv77D_g1tvF9u3FVqnrNbCRL"
    output_folder = "playlist_output"
    max_videos = 10

    download_playlist(playlist_url, output_folder, max_videos)
