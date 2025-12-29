from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import yt_dlp
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Directory to store downloaded files
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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

    # Choose format string depending on requested quality
    if quality == 'best':
        fmt = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    else:
        fmt = 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst'

    ydl_opts = {
        'format': fmt,
        'noplaylist': True,
        'quiet': True,
        # Save to downloads directory; include id/title to reduce collisions
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s-%(id)s.%(ext)s'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # This will download the file to DOWNLOAD_DIR
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                logging.error("Expected downloaded file not found: %s", filename)
                return jsonify({'error': 'Download failed or file not found on server.'}), 500

            # Return a URL that serves the downloaded file
            download_url = url_for('downloaded_file', filename=os.path.basename(filename), _external=True)
            logging.info("Downloaded %s -> %s", video_url, filename)
            return jsonify({'download_url': download_url, 'filename': os.path.basename(filename)})
    except Exception as e:
        logging.exception("An error occurred while processing URL %s: %s", video_url, e)
        return jsonify({'error': 'An unexpected error occurred. Please check the URL or try again later.'}), 500

@app.route('/downloads/<path:filename>')
def downloaded_file(filename):
    # send_from_directory handles content-disposition and safe paths
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    # In production, set debug=False
    app.run(host='0.0.0.0', debug=True)
