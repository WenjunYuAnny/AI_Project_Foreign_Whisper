from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
from transformers import T5ForConditionalGeneration, T5Tokenizer
import pandas as pd
import pytube
from urllib.parse import urlparse, parse_qs

def get_video_name(video_url):
    try:
        video_id = parse_qs(urlparse(video_url).query).get('v', [None])[0]
        if video_id:
            yt = pytube.YouTube(video_url)
            video_name = yt.title
            return video_name
        else:
            st.warning("Invalid YouTube Video URL. Please enter a valid URL.")
            return None
    except Exception as e:
        st.error(f"Error fetching video name: {e}")
        return None

def get_transcript(video_url):
    video_name = get_video_name(video_url)

    try:
        video_id = video_url.split("v=")[1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript, video_name
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None, video_name

def translate(original_script_text):
    model_name = "t5-base"
    tokenizer = T5Tokenizer.from_pretrained(model_name, model_max_length=1024)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    task_prefix = f"translate English to French: "
    inputs = tokenizer(task_prefix + original_script_text, return_tensors="pt", padding=True)
    output_sequences = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        do_sample=False,
        max_length=200,
    )
    translated_script_text = tokenizer.batch_decode(output_sequences, skip_special_tokens=True)
    return translated_script_text[0]

def display_transcript(transcript):
    if transcript:
        df = pd.DataFrame(transcript)
        df['start_time'] = pd.to_datetime(df['start'], unit='s').dt.time
        df['end_time'] = pd.to_datetime(df['start'] + df['duration'], unit='s').dt.time

        # Translate subtitles to French and add a new column
        df[f'Translated French'] = df['text'].apply(translate)
        df = df.rename(columns = {'start_time': 'Start Time', 'end_time': "End Time", 'text' : 'Original'})
        st.table(df[['Start Time', 'End Time', 'Original', f'Translated French']])
    else:
        st.warning("No transcript available.")

def main():
    st.title("YouTube Subtitle Viewer")

    video_url = st.text_input("Enter YouTube Video URL:")

    if st.button("Get Subtitles"):
        if video_url:
            
            transcript, video_name = get_transcript(video_url)
            st.info(f"Fetching subtitles for: {video_name}")
            display_transcript(transcript)
        else:
            st.warning("Please enter a valid YouTube Video URL.")

if __name__ == "__main__":
    main()
