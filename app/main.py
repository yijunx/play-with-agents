from flask import Flask
from app.apis.internal import bp as internal_bp
from app.apis.chat import bp as chat_bp
from flask_cors import CORS


app = Flask(__name__)

cors = CORS(app)

app.register_blueprint(internal_bp)
app.register_blueprint(chat_bp)
