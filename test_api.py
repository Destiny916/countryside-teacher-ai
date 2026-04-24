import os
from dotenv import load_dotenv
load_dotenv()
from model_service.inference import get_vllm_client

print("Testing API connection...")
print(f"API_TYPE: {os.getenv('API_TYPE', 'local')}")

client = get_vllm_client()
print(f"Client type: {type(client)}")

try:
    result = client.chat(messages=[{'role': 'user', 'content': '你好'}])
    print("API call successful!")
    print(f"Response: {result}")
except Exception as e:
    print(f"API call failed: {e}")
