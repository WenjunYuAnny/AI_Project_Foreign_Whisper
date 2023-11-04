import os
from moviepy.editor import VideoFileClip
import whisper

#extract audio from video
def audio_from_video(video_path, audio_output_path):
    video_clip = VideoFileClip(video_path)
    video_clip.audio.write_audiofile(audio_output_path)
    video_clip.close()

#transcribe the audio to text
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    #print(result["text"])
    return result

def transcribe_video(video_path, audio_dir_path, transcript_dir_path):
    filename = os.path.basename(video_path)
    audio_filename = os.path.splitext(filename)[0] + ".mp3"
    audio_output_path = os.path.join(audio_dir_path, audio_filename)
            
    #extract audio from the specific video
    audio_from_video(video_path, audio_output_path)
    print(f"Extracted audio from {filename}")

    #transcribe audio to text for the specifc audio
    transcript = transcribe_audio(audio_output_path)

    #save the transcript
    transcript_filename = os.path.splitext(filename)[0] + ".txt"
    transcript_output_path = os.path.join(transcript_dir_path, transcript_filename)
    with open(transcript_output_path, 'w') as f:
        f.write(transcript["text"])
    print(f"Saved transcript from {filename}")

def transcribe_video_dir(video_dir_path, audio_dir_path, transcript_dir_path):
    os.makedirs(audio_dir_path, exist_ok=True)
    os.makedirs(transcript_dir_path, exist_ok=True)
    for filename in os.listdir(video_dir_path):
        if filename.endswith('.mp4'):
            video_path = os.path.join(video_dir_path, filename)
            transcribe_video(video_path, audio_dir_path, transcript_dir_path)
    print("all videos transcribed")

if __name__ == "__main__":
    video_dir_path = "downloads"
    audio_dir_path = "audio"
    transcript_dir_path = "transcript"
    transcribe_video_dir(video_dir_path, audio_dir_path, transcript_dir_path)



    