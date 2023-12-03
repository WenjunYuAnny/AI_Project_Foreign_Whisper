import whisper
import os
import scipy
import numpy as np
import librosa
from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import AutoProcessor, BarkModel
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from pytube import YouTube

IMAGEMAGICK_PATH = r"D:/Programs/ImageMagick-7.1.1-Q16-HDRI/magick.exe"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_PATH})

#this file is to compile the process from a youtube link to a video with subtitles and audio in French

#download video from a Youtube link
def download_video(video_url, output_path):
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    print(f"Downloading video: {yt.title}")
    video_filepath = stream.download(output_path)
    return video_filepath

#extract audio from video using moviepy
def audio_from_video(video_path, audio_output_path):
    video_clip = VideoFileClip(video_path)
    video_clip.audio.write_audiofile(audio_output_path)
    video_clip.close()

#transcribe audio to texts using whisper
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result

#turn the transcibe result to a list of strings
def segments_to_text_list(transcribe_result):
    segments = transcribe_result['segments']
    segment_texts = [segment['text'] for segment in segments]
    return segment_texts

#translate texts to French using t5-base model
def translate(original_script_text):
    model_name = "t5-base"
    tokenizer = T5Tokenizer.from_pretrained(model_name, model_max_length=1024)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    task_prefix = "translate English to French: "
    inputs = tokenizer([task_prefix + line for line in original_script_text], return_tensors="pt", padding=True)
    output_sequences = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        do_sample=False,
        max_length=200,
    )
    translated_script_text = tokenizer.batch_decode(output_sequences, skip_special_tokens=True)
    # print(translated_script_text)
    return translated_script_text

#build the translated subtitles as a list of dictionaries with start_time, end_time and translated_text
def build_translated_subtitles(transcribe_result, translated_texts):
    segments = transcribe_result['segments']
    subtites = []
    for segment, translated_text in zip(segments, translated_texts):
        current_subtitle = {
            "start": segment["start"],
            "end": segment["end"],
            "text": translated_text}
        subtites.append(current_subtitle)
    return subtites

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

def foreign_whisper(video_url, project_dir):
    video_path = download_video(video_url, project_dir)
    filename = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(project_dir, filename + "_audio.wav")
    audio_from_video(video_path, audio_path)
    transcribe_result = transcribe_audio(audio_path)
    original_texts = segments_to_text_list(transcribe_result)
    translated_texts = translate(original_texts)
    subtitles = build_translated_subtitles(transcribe_result, translated_texts)
    audio_translated_output_path = os.path.join(project_dir, filename + "_audio_translated.wav")
    text_to_speech(subtitles, audio_translated_output_path)
    output_path = os.path.join(project_dir, filename + "_translated.mp4")
    output_video(video_path, audio_translated_output_path, subtitles, output_path)
    print("translation done!")

project_dir = "test"
video_url = "https://www.youtube.com/watch?v=nBpPe9UweWs"
foreign_whisper(video_url, project_dir)
