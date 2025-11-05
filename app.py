import requests
import openai
import os
from moviepy.editor import TextClip, concatenate_videoclips
from gtts import gTTS
from datetime import datetime
import schedule
import time

# === YOUR CONFIG ===
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_trend():
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=PK"
    data = requests.get(url).text
    start = data.find("<title>") + 7
    end = data.find("</title>", start)
    return data[start:end]

def generate_script(topic):
    prompt = f"Write a viral 60-second YouTube Short script about {topic}, including a strong hook, main points, and call to action."
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def make_video(text):
    tts = gTTS(text)
    tts.save("voice.mp3")

    clips = []
    for i, line in enumerate(text.split(".")):
        if line.strip():
            clip = TextClip(line, fontsize=60, color='white', size=(1080, 1920), bg_color='black', duration=3)
            clips.append(clip)
    video = concatenate_videoclips(clips)
    video.write_videofile("video.mp4", fps=24, audio="voice.mp3")

def send_to_telegram(message, file_path=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

    if file_path:
        url_file = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
        with open(file_path, "rb") as video:
            requests.post(url_file, data={"chat_id": CHAT_ID}, files={"video": video})

def job():
    topic = get_trend()
    script = generate_script(topic)
    make_video(script)
    send_to_telegram(f"🎬 Today's topic: {topic}\n\n{script}", "video.mp4")

# Run daily at 3pm Pakistan time
schedule.every().day.at("10:00").do(job)  # 10:00 UTC = 3:00 PKT

while True:
    schedule.run_pending()
    time.sleep(60)
