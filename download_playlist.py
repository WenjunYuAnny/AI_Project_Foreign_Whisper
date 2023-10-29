import os
import json
from pytube import YouTube, Playlist
from pytube.exceptions import AgeRestrictedError
from youtube_transcript_api import YouTubeTranscriptApi

def format_time(seconds):
    # Convert seconds to HH:MM:SS,mmm format
    hh, rem = divmod(seconds, 3600)
    mm, ss = divmod(rem, 60)
    return f"{int(hh):02}:{int(mm):02}:{int(ss):02},{int(1000*(ss-int(ss))):03}"

def json_to_srt(transcript, srt_filepath):
    with open(srt_filepath, 'w', encoding='utf-8') as f:
        for idx, entry in enumerate(transcript, 1):
            start_time = entry['start']
            end_time = start_time + entry['duration']

            f.write(str(idx) + '\n')
            f.write(format_time(start_time) + " --> " + format_time(end_time) + '\n')
            f.write(entry['text'] + '\n\n')

def download_video(video_url, output_path):
    # Fetch the video details using pytube
    yt = YouTube(video_url)

    # Download the highest resolution video
    stream = yt.streams.get_highest_resolution()
    print(f"Downloading video: {yt.title}")
    video_filepath = stream.download(output_path)
    base_filepath = os.path.splitext(video_filepath)[0]
    return base_filepath

def download_caption_convert_to_srt(video_url, video_path):
    # Fetching the transcript using youtube_transcript_api
    video_id = video_url.split("v=")[1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    srt_filepath = video_path + '.srt'
    print(srt_filepath)

    # Saving the transcript to an SRT file
    json_to_srt(transcript, srt_filepath)
    return "Captions downloaded successfully."

def download_from_playlist(url, video_count=10, output_path="./downloads"):
    playlist = Playlist(url)
    for video_url in playlist.video_urls:
        try:
            video_title = download_video(video_url, output_path)
            download_caption_convert_to_srt(video_url, video_title)
            video_count -= 1
            if video_count < 1:
                break
            
        except AgeRestrictedError:
            print(f"Skipped age-restricted video: {video_url}")

if __name__ == "__main__":
    playlist_url = "https://www.youtube.com/playlist?list=PLI1yx5Z0Lrv77D_g1tvF9u3FVqnrNbCRL"
    output_path = 'downloads'
    count = 10
    download_from_playlist(playlist_url, count, output_path)