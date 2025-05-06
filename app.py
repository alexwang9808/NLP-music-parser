from flask import Flask, request, jsonify, send_from_directory
from chatbot import chatting

app = Flask(__name__, static_folder='C:/Users/aaron/NLP-song-recommender')

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
