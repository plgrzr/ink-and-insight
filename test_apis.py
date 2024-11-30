import os
from dotenv import load_dotenv
import requests
from google.cloud import vision
from google.api_core import client_options
import base64
import io
from PIL import Image, ImageDraw

load_dotenv()

def test_mathpix():
    print("Testing Mathpix API...")
    app_id = os.getenv('MATHPIX_APP_ID')
    app_key = os.getenv('MATHPIX_APP_KEY')
    
    # Test URL for Mathpix
    url = 'https://api.mathpix.com/v3/text'
    
    # Sample image with text (base64 encoded)
    sample_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAyADIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigAooqKeYQRPK2dqjJwM0AS0Vx+u+PbLRzGLm0vI0kGQ7x/KPqCTVJ/iToQXcY7sL67B/jQB3VFcPpXxG0bVtQS1iS4RnYKpaP7x9K7igAooooAKKKKACiiigDjviGSLKxwcHzj/I1xtzpcl7p0FxcSPkwCWVyc5VRlj+QNehfECzlvNNtI4V3MJywHrxXN6X4YvbzS7hJ1MduLcwW6nlm4wXPpk5x6ZoA8t1+6i1dpJ4oWiO0IFckgAdOaqWU32W6jm258tgcV3tp4LttLtLdLgLfXjElY0XIwf4j6cVjX/hm4S7mjsYGeFDhC7AZ9zmgDf8PeJNRnvYYvtszRswBUsTj8K9xr5e0+9vNNvY57SVoZUPDKcV7r4S8Wx+JLQq4WO8iH7yMdD6MPQ0AdXRRRQAUUUUAZ+uWxvNKuYV+8UJX6jkfyrz/wAJ3txp1u1xp9n9uugxQrjIwRnPHTAI/Ou71vWbXRLF7q7fCjhVHVj6CvNPBvjKHxB4n1OGXT/sUe4SRASN+5j0HtjPPrQBo6v4m1zVZ0j1PRPscCkFg0mGb0BC5/WsXWNDTWr9L23E0DtGqOEPQ4xkEVu+NvE6aTPHY2uZbkLvdYwcKuQM8epFZ+ha6nh+6S9vYZJLNlIJwQQSMgfXigDkNZ0e40G+NrcEEjlHXow9RVvw14guPD+qR3kGWT7sqZ4dexrvvFiaTruhTrZy7/M+aNlO5WHcEV47QB9OW1xFeW8dxA4eKRQysDwQanrj/h1qTXmgC3kbL2rGL6dxXYUAFFFFAHMeMPDN54ivtOWO4jhtbVmk3yKxLEgAcA+9XNC0W08O6amn2kk0yKxYtMQWJP0AFbtFAHn3xS8OXGr2MN/ZRmWe2BCqoyWU84/CvNdN1e+0i4E1jcPE3fB4P1HQ17/XDeNPA8Wv5vrELFfgfOOgk/8AZvagCt4Y8YWXie3KKDBdoP3kDHkex9RXJ+PfCUnh+/N1bITYXDZQj/lmx5K/0rkLe4n0y+SaF2huIXBBHQg17JoetWXibRVuIlDqy7ZoT1RsUAY/w31Jl+12LtlSpkQenYiu8rzfxH4f1DwfrMep6UXktWYSQyL1U9wf6ivQ7G7jvrOK5hOY5FDCgCeiiigAooooAKKKKACiiigAooooAKKKKAP/2Q=="
    
    headers = {
        'app_id': app_id,
        'app_key': app_key,
        'Content-Type': 'application/json'
    }
    
    data = {
        'src': sample_image,
        'formats': ['text']
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("✅ Mathpix API is working!")
            print("Response:", response.json())
        else:
            print("❌ Mathpix API error:", response.status_code)
            print("Response:", response.text)
    except Exception as e:
        print("❌ Mathpix API error:", str(e))

def test_google_vision():
    print("\nTesting Google Cloud Vision API...")
    api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
    
    try:
        # Create request URL with API key
        url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'
        
        # Create a proper test image with text
        img = Image.new('RGB', (100, 30), color='white')
        d = ImageDraw.Draw(img)
        d.text((10,10), "Hello World", fill='black')
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Convert to base64
        content = base64.b64encode(img_bytes).decode()
        
        # Prepare the request
        request_data = {
            'requests': [
                {
                    'image': {
                        'content': content
                    },
                    'features': [
                        {
                            'type': 'DOCUMENT_TEXT_DETECTION'
                        }
                    ]
                }
            ]
        }
        
        # Make the request
        response = requests.post(url, json=request_data)
        
        if response.status_code == 200:
            print("✅ Google Cloud Vision API is working!")
            result = response.json()
            if 'responses' in result and result['responses']:
                print("Response:", result['responses'][0])
            else:
                print("No text detected in the image")
        else:
            print("❌ Google Cloud Vision API error:", response.status_code)
            print("Response:", response.text)
            
    except Exception as e:
        print("❌ Google Cloud Vision API error:", str(e))

def test_vision_api_key():
    """Test if the Google Cloud Vision API key is valid"""
    api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
    if not api_key:
        print("❌ No Google Cloud API key found in environment variables")
        return False
        
    print(f"Testing API key: {api_key[:10]}...")
    
    # Create a simple test image
    img = Image.new('RGB', (100, 30), color='white')
    d = ImageDraw.Draw(img)
    d.text((10,10), "Test", fill='black')
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    # Convert to base64
    img_base64 = base64.b64encode(img_bytes).decode()
    
    # Test API
    url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'
    payload = {
        'requests': [{
            'image': {
                'content': img_base64
            },
            'features': [{
                'type': 'DOCUMENT_TEXT_DETECTION'
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:200]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error testing API key: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing API Keys...")
    if test_vision_api_key():
        print("✅ Google Cloud Vision API key is valid!")
    else:
        print("❌ Google Cloud Vision API key is invalid!")
    test_mathpix()
    test_google_vision() 