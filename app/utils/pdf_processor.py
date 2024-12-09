import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import os
import base64
from pdf2image import convert_from_path
import io
import hashlib
import json
from typing import Dict, List, Optional, Tuple

CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cached_data"
)
os.makedirs(CACHE_DIR, exist_ok=True)
MAX_WORKERS = 4


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


def process_page(args: Tuple) -> Optional[str]:
    image, page_num = args
    try:
        base64_image = prepare_page_image(image)
        url = f"https://vision.googleapis.com/v1/images:annotate?key={os.environ.get('GOOGLE_CLOUD_API_KEY')}"

        payload = {
            "requests": [
                {
                    "image": {"content": base64_image},
                    "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                }
            ]
        }

        print(f"Processing page {page_num+1}")

        response = requests.post(url, json=payload, timeout=60)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return None

        result = response.json()
        if not result.get("responses"):
            print(f"No text detected on page {page_num+1}")
            return None

        text_annotation = result["responses"][0].get("fullTextAnnotation")
        if not text_annotation:
            return None

        return text_annotation.get("text", "")

    except Exception as e:
        print(f"Error processing page {page_num+1}: {str(e)}")
        return None


def convert_pdf_to_images(file_path: str) -> List:
    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(convert_from_path, file_path)
        return future.result()


def process_pdf_pages(file_path: str, images: List) -> List[str]:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(process_page, (image, i)) for i, image in enumerate(images)
        ]
        return [
            result
            for future in as_completed(futures)
            if (result := future.result()) is not None
        ]


def process_multiple_pdfs(pdf_files: List[str]) -> Dict[str, str]:
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(extract_text_from_pdf, pdf_file): pdf_file
            for pdf_file in pdf_files
            if validate_pdf(pdf_file)
        }
        return {
            pdf_file: future.result()
            for future in as_completed(futures)
            if (pdf_file := futures[future])
        }


def extract_text_from_pdf(file_path: str) -> str:
    try:
        cache_key = get_cache_key(file_path)
        if cached := load_from_cache(cache_key):
            print(f"Using cached response for {file_path}")
            return cached

        images = convert_pdf_to_images(file_path)
        texts = process_pdf_pages(file_path, images)

        if not texts:
            return ""

        full_content = "\n\n".join(texts)
        save_to_cache(cache_key, full_content)
        print(f"Extracted {len(texts)} pages, total length: {len(full_content)}")

        return full_content

    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return ""
