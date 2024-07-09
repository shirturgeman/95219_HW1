import requests
import google.generativeai as genai
import textwrap
from IPython.display import Markdown
from flask import jsonify
import vertexai
from vertexai.preview.vision_models import Image, ImageTextModel
from vertexai.generative_models import GenerativeModel
import io
from gcloud import storage

import os
import base64

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./server_auth.json"


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def upload_image_to_gcs(local_image_path, bucket_name, object_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_image_path)
    print(object_name)
    return f"https://storage.cloud.google.com/hw1website/{object_name}"


def classify_image(question, image_path):
    print(f'====> classify_image: {image_path}')

    try:
        vertexai.init(project="hw1website-428713", location="us-central1")

        model = ImageTextModel.from_pretrained("imagetext@001")
        source_img = Image.load_from_file(location=image_path)
        print(source_img)

        response = model.ask_question(
            image=source_img,
            question=question,
            # Optional parameters
            number_of_results=2,
        )

        to_markdown(response[0])

        print(f'====> response.text: {response[0]}')

        return response[0]

        # return template checked: 
        """return(
            {'result': {
                'classification': 'cat',
                'score': 10
            }, 'image_path': image_path}
        )"""
        
    except Exception as e:
        return jsonify({'message': 'Failed to classify image', 'result': str(e)})