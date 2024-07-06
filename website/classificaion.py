import requests
import google.generativeai as genai
import textwrap
from IPython.display import Markdown
from flask import jsonify

genai.configure(api_key='AIzaSyC016qTmwtlBSZZbbMTD43E2vGYPiNeox4')

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


def classify_image(image_path):
    print(f'====> classify_image: {image_path}')

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # todo: make the question as input
        response = model.generate_content(["What is the main object in the photo?", image_path], stream=True)
        response.resolve()

        to_markdown(response.text)
        return response.text
        
    except Exception as e:
        return jsonify({'message': 'Failed to classify image', 'result': str(e)})




