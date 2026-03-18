from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import logging
import os
from utils.video_gen import VideoGenerator
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

vg = VideoGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    video_url = data.get('url')
    quality = data.get('quality')

    if not video_url:
        return jsonify({'error': 'Video URL is required'}), 400

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if quality == 'best' else 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_download_url = info.get('url', None)
            if video_download_url:
                return jsonify({'download_url': video_download_url})
            else:
                logging.error(f"Could not extract download link for URL: {video_url}")
                return jsonify({'error': 'Could not get download link. The video may be private or unavailable.'}), 500
    except Exception as e:
        logging.exception(f"An error occurred while processing URL {video_url}: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please check the URL or try again later.'}), 500

@app.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.get_json()
    topic = data.get('topic')
    text = data.get('text')
    mode = data.get('mode', 'random') # 'random', 'topic', 'text'

    try:
        if mode == 'text' and text:
            script = text
        else:
            script = vg.generate_script(topic if mode == 'topic' else None)

        filename = f"video_{os.urandom(4).hex()}.mp4"
        vo_path = vg.text_to_speech(script, filename=f"vo_{filename}.mp3")
        video_path = vg.create_video(script, vo_path, output_filename=filename)

        return jsonify({
            'success': True,
            'video_url': f"/output/{filename}",
            'script': script
        })
    except Exception as e:
        logging.exception(f"Video generation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/output/<path:filename>')
def serve_video(filename):
    return send_from_directory('output', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
