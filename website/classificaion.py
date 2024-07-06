import requests
import google.generativeai as genai

genai.configure(api_key='AIzaSyC016qTmwtlBSZZbbMTD43E2vGYPiNeox4')


def classify_image(image_path):
    print(f'====> classify_image: {image_path}')

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(["What is the main object in the photo?", image_path], stream=True)
        response.resolve()

        print(f'====> response: {response._result.content}')
        return response._result.content
        
    except Exception as e:
        return {'error': 'Failed to classify image'}




