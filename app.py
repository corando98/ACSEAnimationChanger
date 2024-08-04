import os
import sys
import threading
import requests
import urllib3
import webbrowser
import shutil
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from moviepy.editor import VideoFileClip
from werkzeug.serving import make_server

# Determine if the app is running as a bundled executable or as a script
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.abspath(".")

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(base_dir, 'videos')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the videos directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Disable SSL warnings
urllib3.disable_warnings()

# Embed the HTML template (empty for now)
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACSE Animation Changer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            transition: background-color 0.3s, color 0.3s;
            background-color: #181818;
            color: #f1f1f1;
        }
        .dark-mode {
            background-color: #181818;
            color: #f1f1f1;
        }
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .video-item {
            border: 1px solid #444;
            padding: 10px;
            border-radius: 8px;
            background-color: #333;
            transition: background-color 0.3s, border-color 0.3s;
        }
        .video-item h2 {
            font-size: 16px;
            margin: 0 0 10px;
        }
        .video-item p {
            margin: 5px 0;
        }
        .video-item video {
            width: 100%;
            height: auto;
            margin-bottom: 10px;
        }
        .video-item button {
            display: block;
            width: 100%;
            padding: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-top: 5px;
        }
        .video-item button:hover {
            background-color: #0056b3;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #444;
            background-color: #333;
            transition: background-color 0.3s, border-color 0.3s;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            color: #f1f1f1;
        }
        .tab button:hover {
            background-color: #444;
        }
        .tab button.active {
            background-color: #555;
        }
        .tabcontent {
            display: none;
            padding: 6px 12px;
            border: 1px solid #444;
            border-top: none;
            transition: background-color 0.3s, border-color 0.3s;
            background-color: #333;
        }
        .sort-options, .search-bar {
            margin-bottom: 20px;
        }
        .pagination {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        .pagination button {
            padding: 10px 20px;
            margin: 0 5px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .pagination button:hover {
            background-color: #0056b3;
        }
        .quit-button {
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 10px 20px;
            background-color: #ff4d4d;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .quit-button:hover {
            background-color: #d11a1a;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
        }
        .form-group input {
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
        }
    </style>
</head>
<body class="dark-mode">
    <h1>ACSE Animation Changer</h1>
    <button class="quit-button" onclick="quitProgram()">Quit</button>
    <div class="tab">
        <button class="tablinks" onclick="openTab(event, 'Download')">Download Videos</button>
        <button class="tablinks" onclick="openTab(event, 'Manage')">Manage Videos</button>
    </div>

    <div id="Download" class="tabcontent">
        <h2>Available Videos from SteamDeckRepo</h2>
        <div class="search-bar">
            <label for="search">Search:</label>
            <input type="text" id="search" onkeypress="searchKeyPress(event)">
        </div>
        <div class="sort-options">
            <label for="sort">Sort by:</label>
            <select id="sort" onchange="changeSort()">
                <option value="downloads-desc">Most Downloaded</option>
                <option value="trending">Trending</option>
                <option value="likes-desc">Most Liked</option>
                <option value="created_at-desc">Uploaded (Newest)</option>
                <option value="created_at-asc">Uploaded (Oldest)</option>
                <option value="random">Random</option>
            </select>
        </div>
        <div id="external-video-list" class="video-grid"></div>
        <div class="pagination">
            <button id="prevPage" onclick="changePage(-1)" style="display: none;">Previous</button>
            <button id="nextPage" onclick="changePage(1)" style="display: none;">Next</button>
        </div>
    </div>

    <div id="Manage" class="tabcontent">
        <h2>Downloaded Videos</h2>
        <div class="form-group">
            <label for="replacePath">Replace Path:</label>
            <input type="text" id="replacePath" placeholder="Specify the path to replace or leave empty to auto-detect">
        </div>
        <div id="video-list" class="video-grid">
            {% for video in videos %}
            <div class="video-item" id="{{ video }}-item">
                <h2>{{ video.replace('.webm', '') }}</h2>
                <video controls>
                    <source src="{{ url_for('preview', filename=video) }}" type="video/webm">
                    Your browser does not support the video tag.
                </video>
                <button onclick="replaceVideo('{{ video }}')">Replace</button>
                <button onclick="deleteVideo('{{ video }}')">Delete</button>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        let currentPage = 1;
        let totalPages = 1;

        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }

        function searchKeyPress(event) {
            if (event.key === "Enter") {
                console.log("Search triggered");
                currentPage = 1;
                fetchExternalVideos();
            }
        }

        function changeSort() {
            console.log("Sort changed");
            currentPage = 1;
            fetchExternalVideos();
        }

        async function fetchExternalVideos() {
            const sortOption = document.getElementById('sort').value;
            const searchQuery = document.getElementById('search').value;
            console.log(`Fetching videos with sort: ${sortOption}, search: ${searchQuery}, page: ${currentPage}`);
            const response = await fetch(`/fetch_videos?page=${currentPage}&sort=${sortOption}&search=${searchQuery}`);
            const { posts, links, meta } = await response.json();
            const videoListDiv = document.getElementById('external-video-list');
            videoListDiv.innerHTML = '';

            posts.forEach(video => {
                const videoItem = document.createElement('div');
                videoItem.className = 'video-item';
                videoItem.innerHTML = `
                    <h2>${video.title}</h2>
                    <p>Author: ${video.user.steam_name}</p>
                    <p>Downloads: ${video.downloads}</p>
                    <p>Uploaded: ${new Date(video.created_at).toLocaleDateString()}</p>
                    <video controls>
                        <source src="${video.video}" type="video/webm">
                        Your browser does not support the video tag.
                    </video>
                    <button onclick="downloadVideo('${video.video}', '${video.title}')">Download</button>
                `;
                videoListDiv.appendChild(videoItem);
            });

            // Show "Next" button only if there are 12 posts
            document.getElementById('nextPage').style.display = posts.length === 12 ? 'inline' : 'none';
            document.getElementById('prevPage').style.display = currentPage > 1 ? 'inline' : 'none';
        }

        async function downloadVideo(url, title) {
            console.log(`Downloading video: ${title} from ${url}`);
            const response = await fetch('/download_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url, title })
            });
            const data = await response.json();
            alert(data.message);
            location.reload();
        }

        async function replaceVideo(filename) {
            console.log(`Replacing video: ${filename}`);
            const replacePath = document.getElementById('replacePath').value;
            const response = await fetch('/convert_replace', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename, replacePath })
            });
            const data = await response.json();
            alert(data.message);
        }

        async function deleteVideo(filename) {
            console.log(`Deleting video: ${filename}`);
            const response = await fetch('/delete_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename })
            });
            const data = await response.json();
            alert(data.message);
            document.getElementById(`${filename}-item`).style.display = 'none';
        }

        function changePage(direction) {
            currentPage += direction;
            if (currentPage < 1) currentPage = 1;
            console.log(`Changing to page: ${currentPage}`);
            fetchExternalVideos();
        }

        function quitProgram() {
            fetch('/shutdown', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(() => {
                window.close();
            });
        }

        document.addEventListener('DOMContentLoaded', () => {
            fetchExternalVideos();
            document.querySelector('.tablinks').click();
            document.getElementById('sort').value = 'downloads-desc'; // Default to Most Downloaded
            changeSort();
        });
    </script>
</body>
</html>

"""

def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()

def download_video(url, path):
    print(f"Downloading video from {url} to {path}")
    response = requests.get(url, stream=True, verify=False)
    with open(path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    print(f"Finished downloading video from {url}")

def find_dynamic_path():
    user_profile = os.environ['USERPROFILE']
    base_path = os.path.join(user_profile, 'AppData', 'Local', 'Packages')
    target_filename = 'Starfield_backup.mp4'
    for root, dirs, files in os.walk(base_path):
        if target_filename in files:
            return os.path.join(root, target_filename)
    return None

@app.route('/fetch_videos')
def fetch_videos_route():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'downloads-desc')
    search = request.args.get('search', '')
    search_query = f"&search={search}" if search else ""
    url = f'https://steamdeckrepo.com/api/posts?page={page}&sort={sort}{search_query}'
    print(f"Fetching videos from {url}")
    response = requests.get(url, verify=False)
    video_list = response.json()
    print(f"Fetched {len(video_list.get('posts', []))} videos")
    return jsonify(video_list)

@app.route('/preview/<filename>')
def preview(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/convert_replace', methods=['POST'])
def convert_replace():
    data = request.json
    filename = data['filename']
    target_path = data.get('replacePath') or find_dynamic_path()
    
    if not target_path:
        return jsonify({'status': 'error', 'message': 'Target path not found'})
    
    webm_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    mp4_path = webm_path.replace('.webm', '.mp4')
    
    if not os.path.exists(mp4_path):
        try:
            print(f"Converting {webm_path} to {mp4_path}")
            clip = VideoFileClip(webm_path)
            clip.write_videofile(mp4_path, codec='libx264')
            print(f"Finished converting {webm_path} to {mp4_path}")
        except Exception as e:
            print(f"Error during conversion: {e}")
            return jsonify({'status': 'error', 'message': str(e)})
    
    print(f"Replacing {target_path} with {mp4_path}")
    
    try:
        if os.path.exists(target_path):
            os.remove(target_path)
            print(f"Removed existing file at {target_path}")
        shutil.copy(mp4_path, target_path)
        print(f"Replaced {target_path} successfully")
        return jsonify({'status': 'success', 'message': 'Boot animation replaced!'})
    except Exception as e:
        print(f"Error replacing file: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("Shutting down Flask server...")
    shutdown_event.set()
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

@app.route('/download_video', methods=['POST'])
def download_video_route():
    data = request.json
    video_url = data['url']
    title = data['title']
    sanitized_title = sanitize_filename(title)
    filename = f"{sanitized_title}.webm"
    download_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        download_video(video_url, download_path)
        return jsonify({'status': 'success', 'message': 'Video downloaded successfully'})
    except Exception as e:
        print(f"Error downloading video: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/delete_video', methods=['POST'])
def delete_video_route():
    data = request.json
    filename = data['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    mp4_path = file_path.replace('.webm', '.mp4')
    if os.path.exists(file_path):
        print(f"Deleting video: {file_path}")
        os.remove(file_path)
        if os.path.exists(mp4_path):
            print(f"Deleting converted video: {mp4_path}")
            os.remove(mp4_path)
        return jsonify({'status': 'success', 'message': 'Video deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'File not found'})

# Function to render the embedded HTML template
@app.route('/')
def index():
    videos = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.webm')]
    print(f"Listing downloaded videos: {videos}")
    return render_template_string(html_template, videos=videos)

# Thread class for Flask server
class FlaskThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5001, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print("Starting Flask server...")
        self.server.serve_forever()

    def shutdown(self):
        print("Shutting down Flask server...")
        self.server.shutdown()

class MainApp:
    def __init__(self):
        # Start Flask server in a separate thread
        self.flask_thread = FlaskThread()
        self.flask_thread.start()

        # Open the web UI in the default browser
        webbrowser.open('http://127.0.0.1:5001/')

    def on_closing(self):
        # Shutdown the Flask server when closing the window
        requests.post('http://127.0.0.1:5001/shutdown')
        self.flask_thread.shutdown()

if __name__ == "__main__":
    shutdown_event = threading.Event()
    app_instance = MainApp()
    shutdown_event.wait()
    print("Main program exiting...")
