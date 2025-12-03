import requests
import sys

print("Testing API connection...")
print(f"Python version: {sys.version}")
print(f"Requests version: {requests.__version__}")

try:
    print("Attempting to connect to http://localhost:8000/api/stocks")
    response = requests.get('http://localhost:8000/api/stocks', timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Content Type: {response.headers.get('Content-Type')}")
    
    # 尝试解析JSON
    try:
        data = response.json()
        print(f"Response JSON (length): {len(data)}")
        if data:
            print(f"First item preview: {data[0] if isinstance(data, list) else data}")
    except Exception as json_error:
        print(f"JSON parsing error: {str(json_error)}")
        print(f"Response content (first 200 chars): {response.text[:200]}")
        
except Exception as e:
    print(f"Connection error: {str(e)}")
    if hasattr(e, 'args'):
        print(f"Error args: {e.args}")
