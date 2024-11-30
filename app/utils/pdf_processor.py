import requests
import os
import base64
from pdf2image import convert_from_path
from PIL import Image
import io

def validate_pdf(file_path):
    """
    Validate if the file is a valid PDF using basic signature check
    """
    try:
        with open(file_path, 'rb') as file:
            # Check PDF signature
            header = file.read(5)
            if header == b'%PDF-':
                return True
            return False
    except Exception as e:
        print(f"Validation error for {file_path}: {str(e)}")
        return False

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF using Mathpix API
    """
    try:
        # Convert PDF to images
        images = convert_from_path(file_path)
        all_text = []
        
        # Process each page
        for i, image in enumerate(images):
            # Save image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Convert to base64
            img_base64 = base64.b64encode(img_byte_arr).decode()
            
            # Send request to Mathpix
            url = 'https://api.mathpix.com/v3/text'
            headers = {
                'app_id': os.environ.get('MATHPIX_APP_ID'),
                'app_key': os.environ.get('MATHPIX_APP_KEY'),
                'Content-Type': 'application/json'
            }
            
            print(f"Using Mathpix credentials - app_id: {headers['app_id']}, app_key: {headers['app_key'][:10]}...")
            
            data = {
                'src': f'data:image/png;base64,{img_base64}',
                'formats': ['text'],
                'ocr': True,
                'rm_spaces': True,
                'enable_tables': True,
                'enable_markdown': True,
                'enable_math': True,
                'enable_handwriting': True
            }
            
            print(f"Sending request to Mathpix for {file_path} page {i+1}")
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code != 200:
                print(f"Error response from Mathpix: {response.status_code}")
                print(f"Response content: {response.text}")
                continue
                
            result = response.json()
            print(f"Mathpix response for page {i+1}: {result}")
            
            if 'error' in result:
                print(f"Mathpix error: {result['error']}")
                if 'error_info' in result:
                    print(f"Error info: {result['error_info']}")
                continue
            
            # Extract content
            text_content = result.get('text', '')
            all_text.append(text_content)
        
        # Combine all text
        full_content = '\n\n'.join(all_text)
        print(f"Extracted text length: {len(full_content)}")
        return full_content
            
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        print(f"Full error details: {str(e.__dict__)}")
        return ""