import time
import json
import base58
import nacl.signing
import nacl.encoding
import requests
from src.helpers.logger import get_custom_logger

logger = get_custom_logger()

HEADERS = {
    'accept': '*/*',
    'content-type': 'application/json',
    'origin': 'https://pump.fun'
}

def generate_keypair():
    signing_key = nacl.signing.SigningKey.generate()
    return signing_key, signing_key.verify_key

def write_to_file(secret_key, token, public_key):
    with open("accounts/generated.txt", "a") as f:
        f.write(f"{token}\n")

def send_request(url, payload=None):
    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload) if payload else None)
        logger.debug(f"Response status: {response.status_code}")
        if response.status_code == 201:
            return response.cookies.get('auth_token')
        else:
            logger.error(f"Failed request with status code {response.status_code} and message: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error in send_request: {e}")
        return None

def login(signing_key, verify_key):
    timestamp = str(int(time.time() * 1000))
    message = f"Sign in to pump.fun: {timestamp}".encode('utf-8')
    signature = signing_key.sign(message).signature

    if not verify_key.verify(message, signature):
        raise Exception("Signature verification failed")

    payload = {
        "address": base58.b58encode(verify_key.encode()).decode('utf-8'),
        "signature": base58.b58encode(signature).decode('utf-8'),
        "timestamp": timestamp,
    }

    access_token = send_request("https://frontend-api.pump.fun/auth/login", payload)
    logger.info(f"Stored access token: {access_token}")
    return access_token

def main():
    signing_key, verify_key = generate_keypair()
    public_key = base58.b58encode(verify_key.encode()).decode('utf-8')
    access_token = login(signing_key, verify_key)
    if access_token:
        write_to_file(signing_key.encode(nacl.encoding.HexEncoder).decode('utf-8'), access_token, public_key)

def call_main_with_delay(generate_amount):
    for _ in range(generate_amount):
        main()


