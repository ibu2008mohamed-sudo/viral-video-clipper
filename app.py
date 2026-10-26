import os
import streamlit as st
import yt_dlp
from moviepy.editor import VideoFileClip

st.set_page_config(page_title="Viral Video Clipper", layout="centered")

st.title("🎬 Viral Video Clipper")
st.write("Paste a video URL to automatically download and trim a clip.")

# Inputs
video_url = st.text_input("Enter Video URL (YouTube, Vimeo, etc.):")
col1, col2 = st.columns(2)
with col1:
    start_time = st.number_input("Start Time (seconds)", min_value=0, value=0)
with col2:
    end_time = st.number_input("End Time (seconds)", min_value=1, value=10)

if st.button("Cut Video"):
    if not video_url:
        st.warning("Please enter a valid URL first.")
    elif start_time >= end_time:
        st.error("Start time must be less than end time.")
    else:
        status = st.empty()
        status.info("Downloading video...")
        
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)
        raw_video_path = os.path.join(output_dir, "raw_video.mp4")
        clip_video_path = os.path.join(output_dir, "clipped_video.mp4")

        try:
            # Step 1: Download Video
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': raw_video_path,
                'overwrites': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            status.info("Trimming video clip...")

            # Step 2: Trim Video
            with VideoFileClip(raw_video_path) as video:
                subclip = video.subclip(start_time, end_time)
                subclip.write_videofile(clip_video_path, codec="libx264", audio_codec="aac")

            status.success("Done!")

            # Step 3: Display & Download
            st.video(clip_video_path)
            with open(clip_video_path, "rb") as file:
                st.download_button(
                    label="Download Clip",
                    data=file,
                    file_name="clip.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            status.error(f"An error occurred: {str(e)}")
