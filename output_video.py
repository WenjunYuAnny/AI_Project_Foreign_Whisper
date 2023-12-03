from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from transformers import AutoProcessor, BarkModel
import scipy
import numpy as np
import librosa
from moviepy.config import change_settings
import os

IMAGEMAGICK_PATH = r"D:/Programs/ImageMagick-7.1.1-Q16-HDRI/magick.exe"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_PATH})

#retrieve timestamp from the translated srt file
def srt_to_subtitles(srt_file_path):
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    subtitles = []
    current_subtitle = {}

    for line in lines:
        line = line.strip()
        if line.isdigit():
            if current_subtitle:
                subtitles.append(current_subtitle)
            current_subtitle = {}
        elif '-->' in line:
            start, end = map(float, line.split(" --> "))
            current_subtitle["start"] = start
            current_subtitle["end"] = end
        elif line:
            current_subtitle["text"] = line
    if current_subtitle:
        subtitles.append(current_subtitle)
    return subtitles

#adjust length of the produced audio in French according to the timestamp
#when producing audio for the 14min video, we actually used Colab to use GPU (see the Colab Notebook text_to_speech_time.ipynb)
def text_to_speech(subtitles, audio_output_path):
    processor = AutoProcessor.from_pretrained("suno/bark-small")
    model = BarkModel.from_pretrained("suno/bark-small")
    model =  model.to_bettertransformer()
    sample_rate = model.generation_config.sample_rate
    voice_preset = "v2/fr_speaker_0"
    pieces = []
    for i, subtitle in enumerate(subtitles):
        print("start: " +  subtitle["text"])
        text = subtitle["text"]
        inputs = processor(text, voice_preset=voice_preset)
        audio_array = model.generate(**inputs)
        audio_array = audio_array.cpu().numpy().squeeze()
        speed_factor = (subtitle["end"] - subtitle["start"]) / len(audio_array) * sample_rate
        print("video_original_length ", subtitle["end"] - subtitle["start"])
        print("output length ", len(audio_array) / sample_rate)
        audio_array = librosa.effects.time_stretch(audio_array, rate=(1/speed_factor))
        pieces.append(audio_array)
        if i < len(subtitles) - 1:
          pause = subtitles[i+1]["start"] - subtitles[i]["end"]
          if pause > 0:
            pause_audio = np.zeros(int(pause * sample_rate))
            pieces.append(pause_audio)
    concatenated_audio = np.concatenate(pieces)
    scipy.io.wavfile.write(audio_output_path, rate=sample_rate, data=concatenated_audio)

#put the video, audio and subtitles all together
def output_video(video_file_path, audio_file_path, subtitles, output_path):
    video = VideoFileClip(video_file_path)
    audio = AudioFileClip(audio_file_path)
    video_width, video_height = video.size
    video = video.set_audio(audio)

    texts = []
    for subtitle in subtitles:
        # print(subtitle['text'])
        text = TextClip(subtitle['text'], fontsize=24, color='white', size=(video_width*6/7, None), method='caption')
        text = text.set_position(('center', video_height*5/6)).set_start(subtitle['start']).set_end(subtitle['end'])
        texts.append(text)

    video = CompositeVideoClip([video] + texts)
    video.write_videofile(output_path)

srt_file_path = "translated_srt/Attorney General Merrick Garland The 60 Minutes Interview.srt"
video_file_path = "downloads/Attorney General Merrick Garland The 60 Minutes Interview.mp4"
filename = os.path.splitext(os.path.basename(srt_file_path))[0]
audio_dir = "translated_audio_time"
audio_file_path = os.path.join(audio_dir, filename + ".wav")
output_dir = "output"
output_path = os.path.join(output_dir, filename + ".mp4")
subtitles = srt_to_subtitles(srt_file_path)
text_to_speech(subtitles, audio_file_path)
output_video(video_file_path, audio_file_path, subtitles, output_path)
