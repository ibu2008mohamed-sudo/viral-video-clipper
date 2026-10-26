import os
import streamlit as st
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

st.set_page_config(page_title="AI Shorts & Viral Clipper", page_icon="🎬", layout="centered")

st.title("🎬 AI Viral Shorts Generator")
st.write("Paste a YouTube URL to automatically extract engaging clips, crop to 9:16 vertical format, and render captions.")

url = st.text_input("Enter YouTube Video URL:")

def get_video_id(url_str):
    if "youtu.be/" in url_str:
        return url_str.split("youtu.be/")[1].split("?")[0]
    elif "watch?v=" in url_str:
        return url_str.split("watch?v=")[1].split("&")[0]
    return None
def download_video(url_str, output_path="temp_video.mp4"):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'overwrites': True,
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'ios', 'android', 'web'],
                'skip': ['hls', 'dash']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'legacyserverconnect': True,
        'nocheckcertificate': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url_str])
    return output_path
def find_best_segment(vid_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid_id)
        best_start = 0
        max_words = 0
        for i, entry in enumerate(transcript):
            start = entry['start']
            words = 0
            for j in range(i, len(transcript)):
                if transcript[j]['start'] - start > 45:
                    break
                words += len(transcript[j]['text'].split())
            if words > max_words:
                max_words = words
                best_start = start
        return best_start, best_start + 45, transcript
    except Exception:
        return 0, 45, []

def crop_to_vertical(clip):
    w, h = clip.size
    target_w = int(h * (9 / 16))
    if target_w > w:
        target_w = w
    x1 = (w - target_w) // 2
    return clip.crop(x1=x1, width=target_w, y1=0, height=h)

if st.button("Generate AI Short"):
    if not url:
        st.error("Please enter a valid YouTube URL.")
    else:
        video_id = get_video_id(url)
        if not video_id:
            st.error("Invalid YouTube link format.")
        else:
            with st.spinner("Analyzing transcript & finding viral moments..."):
                start_time, end_time, transcript = find_best_segment(video_id)
                st.info(f"Selected clip timing: {int(start_time)}s to {int(end_time)}s")

            with st.spinner("Downloading video stream..."):
                raw_video = download_video(url)

            with st.spinner("Cropping to 9:16 Shorts format and adding captions..."):
                full_clip = VideoFileClip(raw_video)
                trimmed = full_clip.subclip(start_time, end_time)
                vertical_clip = crop_to_vertical(trimmed)

                subtitle_clips = [vertical_clip]
                for item in transcript:
                    t_start = item['start'] - start_time
                    t_dur = item['duration']
                    if 0 <= t_start < (end_time - start_time):
                        txt = TextClip(
                            item['text'], 
                            fontsize=28, 
                            color='yellow', 
                            font='Arial-Bold',
                            stroke_color='black',
                            stroke_width=2,
                            method='caption',
                            size=(vertical_clip.w - 40, None)
                        ).set_start(t_start).set_duration(t_dur).set_position(('center', 'bottom'))
                        subtitle_clips.append(txt)

                final_output = CompositeVideoClip(subtitle_clips)
                output_filename = "viral_short.mp4"
                final_output.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24)

            st.success("Your AI Short is ready!")
            st.video(output_filename)

            with open(output_filename, "rb") as file:
                st.download_button(
                    label="Download Short (.mp4)",
                    data=file,
                    file_name="viral_short.mp4",
                    mime="video/mp4"
                )
