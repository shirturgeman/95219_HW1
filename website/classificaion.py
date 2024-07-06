import requests

def classify_image(image_path):
    api_key = 'AIzaSyC016qTmwtlBSZZbbMTD43E2vGYPiNeox4' # we know this should be in .env file 
    url = 'https://aistudio.google.com/api/v1/gemini/1.5-flash/classify'

    with open(image_path, 'rb') as image_file:
        files = {'image': image_file}
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to classify image'}
