import os
import requests
from gtts import gTTS
from moviepy.editor import *
from PIL import Image
from io import BytesIO
import numpy as np

# ---------- 配置 ----------
WIDTH, HEIGHT = 1080, 1920
OUTPUT_FILE = "output.mp4"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

ASSETS = {
    "励志": "https://files.catbox.moe/8m7o6f.mp3",
    "悲伤": "https://files.catbox.moe/ahgj1r.mp3",
    "温柔": "https://files.catbox.moe/vtk7oi.mp3",
    "孤独": "https://files.catbox.moe/xz5s2m.mp3",
    "希望": "https://files.catbox.moe/1p4lhm.mp3",
}

# ---------- 情绪识别 ----------
def detect_emotion(text):
    if any(w in text for w in ["努力", "奋斗", "拼", "梦想", "坚持"]):
        return "励志"
    elif any(w in text for w in ["痛", "泪", "心碎", "悲伤", "失望"]):
        return "悲伤"
    elif any(w in text for w in ["温柔", "喜欢", "甜", "安静"]):
        return "温柔"
    elif any(w in text for w in ["夜", "孤单", "寂寞", "黑暗"]):
        return "孤独"
    else:
        return "希望"

# ---------- 生成 AI 背景 ----------
def generate_ai_background(text, emotion):
    print("🎨 正在生成 AI 背景图...")
    prompt = f"一张{emotion}氛围的夜景照片，主题：{text}，竖屏高清风格"
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).resize((WIDTH, HEIGHT))
    img.save("background.jpg")
    print("✅ 背景图已生成")

# ---------- 中文语音 ----------
def create_voice(text):
    print("🎙️ 正在生成语音...")
    tts = gTTS(text, lang="zh-cn")
    tts.save("voice.mp3")

# ---------- 字幕生成 ----------
def create_dynamic_subtitles(text, total_duration):
    words = list(text)
    clips = []
    per_word = total_duration / max(len(words), 1)

    for i, w in enumerate(words):
        color = f"rgb({np.random.randint(180,255)}, {np.random.randint(180,255)}, 255)"
        txt_clip = TextClip(
            w,
            fontsize=95,
            color=color,
            font=FONT_PATH,
            method='caption',
            size=(WIDTH - 200, None),
            align='center'
        ).set_position(('center', HEIGHT/2 - 150)).set_duration(per_word)
        txt_clip = txt_clip.crossfadein(0.4).crossfadeout(0.4)
        clips.append(txt_clip.set_start(i * per_word))
    return clips

# ---------- 背景动态光影 ----------
def flicker_effect(get_frame, t):
    frame = get_frame(t).astype(np.float32)
    intensity = 1 + 0.02 * np.sin(2 * np.pi * t)
    frame = np.clip(frame * intensity, 0, 255)
    return frame.astype('uint8')

# ---------- 主程序 ----------
def main():
    text = input("请输入视频文本：")
    emotion = detect_emotion(text)
    print(f"🎭 检测到情绪：{emotion}")

    # 步骤执行
    create_voice(text)
    generate_ai_background(text, emotion)

    voice = AudioFileClip("voice.mp3")
    duration = voice.duration

    # 背景视频加动态效果
    bg = ImageClip("background.jpg").set_duration(duration).fl(flicker_effect)

    # 背景音乐 + 语音
    music = AudioFileClip(ASSETS[emotion]).volumex(0.25)
    dynamic_music = music.audio_fadein(1).audio_fadeout(1)
    final_audio = CompositeAudioClip([dynamic_music, voice.volumex(1.3)]).set_duration(duration)

    # 字幕
    subtitles = create_dynamic_subtitles(text, duration)

    # 合成
    final = CompositeVideoClip([bg, *subtitles]).set_audio(final_audio).resize((WIDTH, HEIGHT))

    print("🎬 正在渲染视频...")
    final.write_videofile(OUTPUT_FILE, fps=24, codec='libx264', audio_codec='aac')
    print("✅ 视频生成完成：output.mp4")

if __name__ == "__main__":
    main()
