import os
from moviepy.editor import *
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import random

def text_to_video(text, output_file="output.mp4"):
    # 生成语音
    tts = gTTS(text, lang='zh-cn')
    tts.save("voice.mp3")

    # 背景颜色随机
    color = random.choice(["#0f0f0f", "#1a1a2e", "#2c3e50", "#3b3b98"])
    img = Image.new('RGB', (720, 1280), color=color)
    d = ImageDraw.Draw(img)

    # 绘制文本（自动换行）
    font = ImageFont.load_default()
    lines = []
    line = ""
    for word in text:
        if d.textlength(line + word, font=font) > 600:
            lines.append(line)
            line = word
        else:
            line += word
    lines.append(line)

    y = 500
    for line in lines:
        d.text((60, y), line, fill=(255,255,255), font=font)
        y += 40

    img.save("background.jpg")

    # 合成视频
    audio = AudioFileClip("voice.mp3")
    image = ImageClip("background.jpg").set_duration(audio.duration)
    video = image.set_audio(audio)
    video.write_videofile(output_file, fps=24)

if __name__ == "__main__":
    text = input("请输入要生成的视频文字：")
    text_to_video(text)
