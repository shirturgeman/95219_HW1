import textwrap
from IPython.display import Markdown
from flask import jsonify
import vertexai
from vertexai.preview.vision_models import Image, ImageTextModel
import os
import json

with open('server_auth.json') as f:
    server_auth = json.load(f)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./server_auth.json"
project_name = server_auth["project_id"]

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


def classify_image(question, image_path):
    print(f'====> classify_image: {image_path}')

    try:

        vertexai.init(project=project_name, location="us-central1")

        model = ImageTextModel.from_pretrained("imagetext@001")
        source_img = Image.load_from_file(location=image_path)
        print(source_img)

        response = model.ask_question(
            image=source_img,
            question=question,
            # Optional parameters
            number_of_results=1,
        )
        answer = response.pop()
        to_markdown(answer)

        print(f'====> response.text: {answer}')

        return(
            {'result': {
                'classification': answer,
                'score': 10
            }, 'image_path': image_path}
        )

        # return template checked: 
        """return(
            {'result': {
                'classification': 'cat',
                'score': 10
            }, 'image_path': image_path}
        )"""
        
    except Exception as e:
        return jsonify({'message': 'Failed to classify image', 'result': str(e)})