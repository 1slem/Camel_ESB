from flask import Flask, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)
