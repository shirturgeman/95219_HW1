from flask import Blueprint, redirect, render_template, request, flash, jsonify, send_file, url_for
from flask_login import login_required, current_user
from . import db
import json
from werkzeug.utils import secure_filename
from .classificaion import classify_image
import os
import time
import random

app_start_time = time.time()
processed_jobs = {'success': 0, 'fail': 0, 'running': 0, 'queued': 0}

request_id = 0
request_results = {}

_app = Blueprint('_app', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@_app.context_processor
def inject_user():
    return dict(user=current_user)

@_app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("index.html", user=current_user)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@_app.route('/upload_image', methods=['POST'])
@login_required
def upload_file():

    request_id =+ 1

    if 'file' not in request.files:
        return jsonify({'message': 'No file part', 'result': ''})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file', 'result': ''})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(UPLOAD_FOLDER):
            try:
                os.makedirs(UPLOAD_FOLDER)
            except OSError as e:
                return jsonify({'message': 'Failed to create upload directory', 'result': str(e)})

        try:
            if not os.path.exists(filepath):
                file.save(filepath)
        except Exception as e:
            return jsonify({'message': 'Failed to save file', 'result': str(e)})

        question = request.form.get('question')

        result = classify_image(question, filepath)

        request_results[request_id] = result

        processed_jobs['success'] += 1  # Assuming the job is always successful for this example
        
        # TODO: count fails
        return redirect(url_for('_app.get_result', request_id=request_id))

    return jsonify({'message': 'Allowed file types are png, jpg, jpeg, gif', 'result': ''})

@_app.route('/result/<int:request_id>', methods=['GET'])
@login_required
def get_result(request_id):
    # Fetch the result from the mock storage
    result_data = request_results.get(request_id)
    if not result_data:
        return jsonify({'error': {'code': 404, 'message': 'ID not found'}}), 404
    
    result = result_data['result']
    image_path = result_data['image_path']

    # Render the result.html template with result and image_path
    return render_template('result.html', request_id=request_id, result=result, image_path=image_path)

@_app.route('/status', methods=['GET'])
def get_status():
    uptime = int(time.time() - app_start_time)
    status = {
        'uptime': uptime,
        'processed': processed_jobs,
        'health': 'ok',  
        'api_version': 1
    }
    return jsonify(status), 200