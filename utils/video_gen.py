import os
import random
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip
import requests
from dotenv import load_dotenv

load_dotenv()

class VideoGenerator:
    def __init__(self):
        self.temp_dir = "assets"
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "audio"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "video"), exist_ok=True)
        os.makedirs("output", exist_ok=True)

    def generate_script(self, topic=None):
        knowledge_data = [
            {"topic": "Laba-laba", "fact": "Tahukah kamu? Laba-laba bukan serangga. Mereka termasuk dalam kelas arachnida karena memiliki delapan kaki, sedangkan serangga hanya enam."},
            {"topic": "Matahari", "fact": "Matahari adalah bintang yang sangat besar. Saking besarnya, sekitar satu juta planet Bumi bisa muat di dalamnya."},
            {"topic": "Madu", "fact": "Madu adalah satu-satunya makanan yang tidak pernah basi. Arkeolog menemukan madu di makam Mesir kuno yang masih layak dimakan setelah 3000 tahun."},
            {"topic": "Oksigen", "fact": "Meskipun oksigen penting untuk kita, sekitar 70% oksigen di Bumi sebenarnya dihasilkan oleh laut, terutama oleh fitoplankton."},
            {"topic": "Otak Manusia", "fact": "Otak manusia menghasilkan listrik yang cukup untuk menyalakan lampu bohlam kecil saat kita sedang terjaga."}
        ]

        if topic:
            selected = next((item for item in knowledge_data if topic.lower() in item['topic'].lower()), None)
            if not selected:
                # In a real app, we'd call GPT here
                return f"Berikut adalah informasi tentang {topic}: {topic} adalah subjek yang menarik untuk dipelajari lebih lanjut dalam bidang pengetahuan umum."
        else:
            selected = random.choice(knowledge_data)

        return selected['fact']

    def text_to_speech(self, text, filename="voiceover.mp3"):
        filepath = os.path.join(self.temp_dir, "audio", filename)
        tts = gTTS(text=text, lang='id')
        tts.save(filepath)
        return filepath

    def create_video(self, script, voiceover_path, output_filename="output_video.mp4"):
        audio = AudioFileClip(voiceover_path)
        duration = audio.duration

        width, height = 720, 1280

        # Background: Try to use a solid color with some variation or an image if available
        background = ColorClip(size=(int(width), int(height)), color=(20, 20, 40), duration=duration)

        # Subtitles
        words = script.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + " " + word) < 15:
                current_line += " " + word
            else:
                lines.append(current_line.strip())
                current_line = word
        lines.append(current_line.strip())

        clips = [background]

        # Instead of one big TextClip, maybe multiple smaller ones or just one that works
        # Let's try to fix the TextClip by specifying a full size
        try:
            # MoviePy 2.x might need specific parameters
            txt_clip = TextClip(
                text="\n".join(lines),
                font_size=60,
                color='yellow',
                # method='caption' is often where it fails if size is weird
                size=(int(width * 0.9), int(height * 0.6)),
                duration=duration
            ).with_position('center')
            clips.append(txt_clip)
        except Exception as e:
            print(f"TextClip error: {e}")
            # Even more basic fallback: just show the text as several ColorClips for now?
            # No, let's try to fix the TextClip call.
            # Some versions of moviepy/PIL have issues with None in size.
            pass

        # Add background music if exists
        # For now, we'll skip music until we have a file, or create a dummy beep?

        video = CompositeVideoClip(clips)
        video = video.with_audio(audio)

        output_path = os.path.join("output", output_filename)
        video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        return output_path

if __name__ == "__main__":
    vg = VideoGenerator()
    script = vg.generate_script()
    vo = vg.text_to_speech(script)
    video = vg.create_video(script, vo)
    print(f"Video saved at: {video}")
