import os
import glob
import math
import warnings
import streamlit as st
import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip

# Suppress yellow warning messages
warnings.filterwarnings("ignore")

# Streamlit Page Config
st.set_page_config(page_title="AI Video Clipper", page_icon="🎬", layout="wide")

st.title("🎬 Viral Short Clip Generator")
st.write("Paste any video link below to automatically generate viral clips!")

# Input Controls
video_url = st.text_input("Enter Video Link (YouTube, Vimeo, direct MP4, etc.):")

col1, col2 = st.columns(2)
with col1:
    clip_count = st.radio("Number of clips to generate:", options=[6, 10], index=0)
with col2:
    clip_duration = st.slider("Clip Duration (seconds):", min_value=15, max_value=60, value=30)

def download_video(url, output_dir="temp_dir"):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'format': 'mp4/bestvideo+bestaudio/best',
        'outtmpl': os.path.join(output_dir, 'input_video.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return os.path.join(output_dir, 'input_video.mp4')

if st.button("Generate Clips ✂️"):
    if not video_url:
        st.error("Please enter a valid video link first!")
    else:
        try:
            with st.spinner("Downloading video from link..."):
                raw_video_path = download_video(video_url)

            st.success("Download complete! Processing clips...")

            # Load video to read duration
            clip = VideoFileClip(raw_video_path)
            total_seconds = clip.duration
            clip.close()

            # Calculate interval spacing so clips are spread evenly throughout the video
            interval = (total_seconds - clip_duration) / max(1, (clip_count - 1))
            output_folder = "output_clips"
            os.makedirs(output_folder, exist_ok=True)

            processed_clips = []

            # Create Clips