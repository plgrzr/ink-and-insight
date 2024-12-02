import nltk
import ssl
import os
import sys

def download_nltk_data():
    """Download required NLTK data"""
    try:
        # Create nltk_data directory in project root
        nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')
        os.makedirs(nltk_data_dir, exist_ok=True)
        
        # Clear existing paths and set new one
        nltk.data.path = [nltk_data_dir]

        # Disable SSL verification if needed
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        required_packages = [
            'punkt',
            'stopwords',
            'wordnet',
            'averaged_perceptron_tagger'
        ]
        
        for package in required_packages:
            try:
                nltk.data.find(f'tokenizers/{package}')
                print(f"Package {package} is already downloaded")
            except LookupError:
                print(f"Downloading {package}...")
                nltk.download(package, download_dir=nltk_data_dir, quiet=True)
                print(f"Successfully downloaded {package}")

        # Verify downloads
        for package in required_packages:
            try:
                if package == 'punkt':
                    sent_tokenize("This is a test sentence.")
                elif package == 'stopwords':
                    stopwords.words('english')
                elif package == 'wordnet':
                    from nltk.corpus import wordnet
                    wordnet.synsets('test')
            except Exception as e:
                print(f"Error verifying {package}: {str(e)}")
                raise

    except Exception as e:
        print(f"Error during NLTK data download: {str(e)}")
        print("\nTrying alternative download method...")
        try:
            for package in required_packages:
                nltk.download(package)
        except Exception as e2:
            print(f"Alternative download failed: {str(e2)}")
            sys.exit(1)

if __name__ == "__main__":
    download_nltk_data() 