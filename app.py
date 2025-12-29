from flask import Flask, request, jsonify, render_template, send_from_directory 
import yt_dlp 
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, filename='server.log', format='%(asctime)s - %(levelname)s - %(message)s') 

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
  os.makedirs(DOWNLOAD_FOLDER) 
  
@app.route('/') 
def index(): 
  return render_template('index.html') 
  
@app.route('/download', methods=['POST'])
def download(): 
  data = request.get_json() 
  video_url = data.get('url')
  quality = data.get('quality', 'best') 
  
if not video_url: 
  return jsonify({'error': 'URL is required'}), 400 
  try: 
    ydl_opts = { 
      'format': f'{quality}[ext=mp4]/best[ext=mp4]/best' if quality != 'best' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
      'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
      'noplaylist': True, 
      'quiet': True, 
      'no_warnings': True, 
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      logging.info(f"Fetching info for URL: {video_url}") 
      info = ydl.extract_info(video_url, download=False) 
      video_title = info.get('title', 'video') 
      
      formats = info.get('formats', [info]) 
      best_format = None 
        if quality == 'best':
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4': 
                    best_format = f
                    break 
                    if not best_format: 
                        best_format = info 
                    else: 
                        target_height = int(quality.replace('p', '')) 
available_formats = [f for f in formats if f.get('height') is not None and f.get('vcodec') != 'none']
if not available_formats: 
    return jsonify({'error': 'No video formats found for this URL.'}),500 
    best_format = min(available_formats, key=lambda x: abs(x['height'] - target_height)) download_url = best_format.get('url') if not download_url: return jsonify({'error': 'Could not extract download link. The video may be protected or unavailable.'}), 500 logging.info(f"Successfully found download link for: {video_title}") return jsonify({ 'download_url': download_url, 'title': video_title }) except yt_dlp.utils.DownloadError as e: logging.error(f"yt-dlp download error for URL {video_url}: {str(e)}") return jsonify({'error': f'Failed to process video. It might be private, deleted, or region-locked. Error: {str(e)}'}), 500 except Exception as e: logging.error(f"An unexpected error occurred for URL {video_url}: {str(e)}") return jsonify({'error': 'An unexpected error occurred. Please check the URL or try again later.'}), 500 if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
