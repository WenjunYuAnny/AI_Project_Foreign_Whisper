import os
from pydub import AudioSegment
from pydub.playback import play
from TTS.api import TTS
import torch
from pydub.generators import Sine
import numpy as np

device = "cuda" if torch.cuda.is_available() else "cpu"

def convert_srt_to_speech(srt_file_path, output_audio_path, model_path):
    # Load Coqui TTS synthesizer
    #synthesizer = Synthesizer.load(model_path)
    tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
    # Read the translated SRT file
    with open(srt_file_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    # Split the content into individual subtitles
    subtitles = srt_content.split('\n\n')

    # Create an empty audio segment
    final_audio = AudioSegment.silent(duration=0)
    subtitle_text = ""
    for subtitle in subtitles:
        # Extract start and end times and subtitle text
        subtitle_lines = subtitle.split('\n')
        if len(subtitle_lines) >= 3:
            start_time, end_time = subtitle_lines[1].split(' --> ')
            subtitle_text += ' '.join(subtitle_lines[2:])

            # Synthesize speech for each subtitle
            #audio_list = tts.tts(subtitle_text)
    tts.tts_to_file(subtitle_text,file_path = output_audio_path)
            # Concatenate the list of audio segments
            #for audio_data in audio_list:
                # Convert NumPy array to AudioSegment
                #if isinstance(audio_data, int):
                #    data = audio_data.to_bytes()
                #else:
                #    data = audio_data.tobytes()
                #audio_segment = AudioSegment.from_mono_audiosegments(
                #    AudioSegment(
                #        data,
                #        frame_rate=24000,
                #        sample_width=2,
                #        channels=1
                #    )
                #)
                #final_audio += audio_segment

    # Export the final audio to the specified output path
    #final_audio.export(output_audio_path, format="wav")

    # Play the generated audio
    #play(final_audio)

if __name__ == "__main__":
    srt_file_path = "transcript_srt\Attorney General Merrick Garland The 60 Minutes Interview.srt"
    output_audio_path = "output audio/output_audio.wav"
    model_path = "best_model.pth.tar"

    convert_srt_to_speech(srt_file_path, output_audio_path, model_path)
