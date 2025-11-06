import requests
import re
from config import URL, headers


def check_and_detect(url: str):
    pattern = re.compile(r'https?://(?:www\.)?(?:pinterest\.com/pin/|pin\.it/)[^\s/?]+')
    results = re.findall(pattern, url)
    return results

def get_response(url: str):
    querystring = {"url": url}
    response = requests.get(URL, headers=headers, params=querystring)
    return response

def get_video_or_img_url(response):
    try:
        if response.status_code == 200:
            try:
                response_api = response.json()
                video_or_img_url = response_api['data']['url']
                return video_or_img_url
            except Exception as e:
                print(e)
                return "false_download_video_or_img_url"
        else:
            print(f"failed with status code {response.status_code}")
            print(f"response {response.text[:500]}")
        return "false_response"
    
    except Exception as e:
        return "false_api"
