import requests
import src.capsolver as capsolver
from src.helpers.logger import get_custom_logger

logger = get_custom_logger()
default_endpoint = "https://frontend-api.pump.fun/"
def parse_file(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.read().splitlines()
    except Exception as e:
        logger.critical(f"Error reading {filepath}: {e}")
        return []

def parse_proxies():
    return parse_file('proxies.txt')

def parse_bearer():
    return parse_file('bearer.txt')

def parse_generated():
    return parse_file('accounts/generated.txt')

def parse_texts():
    return parse_file('comment_text.txt')

def parse_nicks():
    return parse_file('accounts/nicknames.txt')

def parse_pics():
    return parse_file('pics.txt')

def parse_pfp():
    return parse_file('accounts/pfp.txt')

def form_headers(token):
    return {
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": f"auth_token={token}",
        "content-type": "application/json",
    }


def post_comment(bearer, mint_address, comment_text, picture_uri=None, proxy=None):
    max_retries = 10
    retry = 0

    headers = form_headers(bearer)
    json_data = {'text': comment_text, 'mint': mint_address}
    if picture_uri:
        json_data['fileUri'] = picture_uri

    while retry < max_retries:
        try:
            proxy_details = proxy.split(':')
            proxy_ip, proxy_port, proxy_username, proxy_password = proxy_details
            proxies = {
                "http": f"http://{proxy_username}:{proxy_password}@{proxy_ip}:{proxy_port}",
                "https": f"http://{proxy_username}:{proxy_password}@{proxy_ip}:{proxy_port}"
            }

            captcha_token = capsolver.capsolver(proxies['http'])
            if not captcha_token:
                continue

            json_data['token'] = captcha_token
            response = requests.post('https://frontend-api.pump.fun/replies', headers=headers, json=json_data, proxies=proxies)

            if verify_comment(mint_address, comment_text):
                logger.info(f"{mint_address} | {response.status_code} | POSTED COMMENT")
                return
            else:
                logger.warn(f"{mint_address} | Retrying...")

        except Exception as e:
            logger.error(f"Error in post_comment: {e}")

        retry += 1

    logger.error(f"{mint_address} | Max retries exceeded for token")

def monitor():
    url = 'https://frontend-api.pump.fun/coins/latest'
    try:
        response = requests.get(url)
        return response.json().get('mint')
    except Exception as e:
        logger.error(f"Error in monitor: {e}")
        return None

def get_koh():
    url = "https://frontend-api.pump.fun/coins/king-of-the-hill?includeNsfw=false"
    try:
        response = requests.get(url)
        return response.json().get('mint')
    except Exception as e:
        logger.error(f"Error in get_koh: {e}")
        return None

def verify_comment(mint, text):
    url = f"https://frontend-api.pump.fun/replies/{mint}?user=123"
    try:
        comment_list = requests.get(url).json()
        for comment in comment_list:
            if text in comment.get('text', ''):
                return True
    except Exception as e:
        logger.error(f"Error in verify_comment: {e}")
    return False



def update_profile(token, nickname, pic):
    headers = form_headers(token)
    payload = {"profileImage": pic, "username": nickname, "bio": ""}
    try:
        response = requests.post("https://frontend-api.pump.fun/users", headers=headers, json=payload)
        if 'error' in str(response.text):
            return response.text
        return True 

            
    except Exception as e:
        logger.error(f"Error in update_profile: {e}")
        return False

def get_random_username():
    api_url = 'https://api.api-ninjas.com/v1/randomuser'
    try:
        response = requests.get(api_url, headers={'X-Api-Key': '2P/w/evhn2lPxJnwosSPaw==2HESr9dDoprQPb8t'})
        if response.status_code == requests.codes.ok:
            return response.json().get('username')
    except Exception as e:
        logger.error(f"Error in get_random_username: {e}")
    return None

def put_like(comment_id, bearer):
    headers = form_headers(bearer)
    try:
        response = requests.post(f"https://frontend-api.pump.fun/likes/{comment_id}", headers=headers)
        return response.status_code
    except Exception as e:
        logger.error(f"Error in put_like: {e}")
        return None


def parse_replies(token_address):
    texts = []
    get_replies_url = f"{default_endpoint}replies/{token_address}?user=EB824fNJVubePFmkrQJpVX2sSF9poGkgQzyt5AQbUeJm"
    r = requests.get(get_replies_url)
    jsoned_replies = r.json()
    for reply in jsoned_replies:
        texts.append(reply['text'].replace('\n', ''))
    with open(f"parsed_comments/comments_{token_address}.txt", "w") as file:
        for text in texts:
            file.write(text + "\n")      
    return True  
