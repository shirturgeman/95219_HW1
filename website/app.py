from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json
from werkzeug.utils import secure_filename
from .classificaion import classify_image
import os

_app = Blueprint('_app', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
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
        print(f'File name: {filename}')
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        print(f'File path: {filepath}')

        if not os.path.exists(UPLOAD_FOLDER):
            try:
                os.makedirs(UPLOAD_FOLDER)
            except OSError as e:
                return jsonify({'message': 'Failed to create upload directory', 'result': str(e)})

        
        try:
            if not os.path.exists(filepath):
                file.save(filepath)
                print(f'File uploaded: {filename}')
                print(f'File path: {filepath}')
            result = classify_image(filepath)
            return jsonify({'message': 'File successfully uploaded', 'result': result})
        except Exception as e:
            print(f'Error saving file: {e}')
            return jsonify({'message': 'Failed to save file', 'result': str(e)})



    return jsonify({'message': 'Allowed file types are png, jpg, jpeg, gif', 'result': ''})