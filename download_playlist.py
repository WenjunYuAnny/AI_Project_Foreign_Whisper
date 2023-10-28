import os
from pytube import YouTube, Playlist
from pytube.exceptions import AgeRestrictedError

def download_video_and_captions(video_url, output_path):
    # Fetch the video details using pytube
    yt = YouTube(video_url)

    # Download the highest resolution video
    stream = yt.streams.get_highest_resolution()
    print(f"Downloading video: {yt.title}")
    video_filepath = stream.download(output_path)

    base_filepath = os.path.splitext(video_filepath)[0]

    # Download English auto-generated captions
    yt.bypass_age_gate()
    
    caption = yt.captions["a.en"]
    if caption:
        caption_file_content = caption.xml_captions
        caption_filepath = f"{base_filepath}_captions.xml"
        with open(caption_filepath, 'w', encoding='utf-8') as f:
            f.write(caption_file_content)
        print(f"Captions downloaded for {yt.title}")
    else:
        print(f"No English captions found for {yt.title}")


def download_from_playlist(url, video_count=10, output_path="./output"):
    playlist = Playlist(url)
    for video_url in playlist.video_urls:
        try:
            output_folder = "output"
            video_title = download_video_and_captions(video_url, output_folder)
            video_count -= 1
            if video_count < 1:
                break
        except AgeRestrictedError:
            print(f"Skipped age-restricted video: {video_url}")

if __name__ == "__main__":
    playlist_url = "https://www.youtube.com/playlist?list=PLI1yx5Z0Lrv77D_g1tvF9u3FVqnrNbCRL"
    output_path = 'output'
    count = 10
    download_from_playlist(playlist_url, count, output_path)