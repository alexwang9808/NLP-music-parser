from flask import Flask, request, jsonify, send_from_directory
from chatbot import chatting
from pathlib import Path

# Get the directory where app.py is located
base_dir = Path(__file__).resolve().parent

static_dir = base_dir / "NLP-song-recommender"
app = Flask(__name__, static_folder=str(static_dir))

#app = Flask(__name__, static_folder='C:/Users/aaron/NLP-song-recommender')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']
    bot_response = chatting(user_message)
    return jsonify(response=bot_response)

if __name__ == '__main__':
    app.run()
