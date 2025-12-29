from flask import Flask, render_template, request, jsonify
import yt_dlp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
