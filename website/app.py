from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json
from werkzeug.utils import secure_filename
from .classificaion import classify_image
import os

_app = Blueprint('_app', __name__)

UPLOAD_FOLDER = 'website/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@_app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("index.html", user=current_user)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@_app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part', 'result': ''})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file', 'result': ''})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        result = classify_image(filepath)
        return jsonify({'message': 'File successfully uploaded', 'result': result})

    return jsonify({'message': 'Allowed file types are png, jpg, jpeg, gif', 'result': ''})