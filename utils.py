import requests

def upload_image_to_imagebb(api_key, image_path):
    url = "https://api.imgbb.com/1/upload"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    with open(image_path, 'rb') as image_file:
        response = requests.post(
            url,
            headers=headers,
            params={'key': api_key},
            files={'image': image_file}
        )

    if response.status_code == 200:
        result = response.json()
        return result['data']['url']
    else:
        return None
