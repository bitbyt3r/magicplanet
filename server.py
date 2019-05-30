from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app)
PLAYLISTDIR = "./playlists"

@app.route("/")
def home():
    playlists = os.listdir(PLAYLISTDIR)
    return render_template("index.html", playlists=playlists, msg="")

@app.route("/display")
def display():
    return render_template("display.html")

@app.route("/upload")
def upload():
    playlists = os.listdir(PLAYLISTDIR)
    return render_template("index.html", playlists=playlists, msg="Upload Successful")

@app.route("/create_playlist")
def create_playlist():
    new_dir = os.path.join(PLAYLISTDIR, request.args.get("playlist"))
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)
    playlists = os.listdir(PLAYLISTDIR)
    return render_template("index.html", playlists=playlists, msg="Playlist Created")

@app.route("/playlist/<path:playlist>")
def playlist(playlist):
    videos = os.listdir(os.path.join(PLAYLISTDIR, playlist))
    return render_template("playlist.html", playlist=playlist, videos=videos)

@app.route("/play/<path:video>")
def play(video):
    socketio.emit("play", video)
    return jsonify({"success": True})

if __name__ == '__main__':
    socketio.run(app)