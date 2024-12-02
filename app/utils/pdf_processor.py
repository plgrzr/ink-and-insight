import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import base64
from pdf2image import convert_from_path
import io
import hashlib
import json
from typing import Dict, List, Optional

CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cached_data"
)
os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_key(file_path: str) -> str:
    with open(file_path, "rb") as file:
        return hashlib.md5(file.read()).hexdigest()


def load_from_cache(cache_key: str) -> Optional[str]:
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r") as file:
            return json.load(file)
    return None


def save_to_cache(cache_key: str, data: str) -> None:
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    with open(cache_file, "w") as file:
        json.dump(data, file)


def validate_pdf(file_path: str) -> bool:
    try:
        with open(file_path, "rb") as file:
            return file.read(5) == b"%PDF-"
    except Exception as e:
        print(f"Validation error for {file_path}: {str(e)}")
        return False


def prepare_page_image(image) -> str:
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    return base64.b64encode(img_byte_arr.getvalue()).decode()


def create_mathpix_request(base64_image: str) -> Dict:
    return {
        "src": f"data:image/png;base64,{base64_image}",
        "formats": ["text"],
        "ocr": True,
        "rm_spaces": True,
        "enable_tables": True,
        "enable_markdown": True,
        "enable_math": True,
        "enable_handwriting": True,
    }


def get_mathpix_headers() -> Dict:
    return {
        "app_id": os.environ.get("MATHPIX_APP_ID"),
        "app_key": os.environ.get("MATHPIX_APP_KEY"),
        "Content-Type": "application/json",
    }


def process_page(args: tuple) -> Optional[str]:
    image, file_path, page_num = args

    try:
        base64_image = prepare_page_image(image)
        headers = get_mathpix_headers()
        data = create_mathpix_request(base64_image)

        print(f"Processing page {page_num+1} of {file_path}")

        response = requests.post(
            "https://api.mathpix.com/v3/text", json=data, headers=headers, timeout=60
        )

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return None

        result = response.json()

        if "error" in result:
            print(f"Mathpix error: {result.get('error')}")
            print(f"Error info: {result.get('error_info', '')}")
            return None

        return result.get("text", "")

    except Exception as e:
        print(f"Error processing page {page_num+1}: {str(e)}")
        return None


def extract_text_from_pdf(file_path: str) -> str:
    try:
        cache_key = get_cache_key(file_path)
        if cached := load_from_cache(cache_key):
            print(f"Using cached response for {file_path}")
            return cached

        images = convert_from_path(file_path)
        texts: List[str] = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_page, (image, file_path, i))
                for i, image in enumerate(images)
            ]

            for future in as_completed(futures):
                if result := future.result():
                    texts.append(result)

        if not texts:
            return ""

        full_content = "\n\n".join(texts)
        save_to_cache(cache_key, full_content)
        print(f"Extracted {len(texts)} pages, total length: {len(full_content)}")

        return full_content

    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return ""
