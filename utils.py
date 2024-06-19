import requests
import base64

def upload_image_to_imagebb(api_key, image_path):
    url = "https://api.imgbb.com/1/upload"
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    payload = {
        'key': api_key,
        'image': encoded_image
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        result = response.json()
        return result['data']['url']
    else:
        print(f"Ошибка {response.status_code}: {response.json()}")
        return None

def get_neko_image():
    response = requests.get('https://nekos.life/api/v2/img/neko')
    if response.status_code == 200:
        data = response.json()
        return data.get('url')
    return None

def get_waifu_image(category='waifu'):
    url = f'https://api.waifu.pics/sfw/{category}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('url')
    return None

def get_nsfw_waifu_image(category='waifu'):
    url = f'https://api.waifu.pics/nsfw/{category}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('url')
    return None
