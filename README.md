# Ink&Insight

A Flask web application that analyzes and compares PDF documents using Google Cloud Vision, Mathpix APIs, and BERT-based semantic analysis to detect similarities in text content, writing style, and semantic flow.

## Features

- PDF document comparison and analysis
- Text and handwriting similarity detection
- Semantic flow analysis using BERT embeddings
- Writing style consistency checking
- Detailed PDF report generation
- Interactive web interface
- Real-time results
- API integration (Google Cloud Vision & Mathpix)

## Prerequisites

- Python 3.8+
- Google Cloud Vision API key
- Mathpix API credentials
- `poppler-utils` for PDF processing
- CUDA-compatible GPU (optional, for faster semantic analysis)

## Quick Start

1. Clone and setup:

   ```bash
   git clone https://github.com/mavericksxx/ink-and-insight.git
   cd ink-and-insight
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   python setup.py  # Downloads required NLTK data
   ```

2. Configure environment:

   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # MATHPIX_APP_ID=your-id
   # MATHPIX_APP_KEY=your-key
   # GOOGLE_CLOUD_API_KEY=your-key
   ```

3. Run application:

   ```bash
   # Development
   python run.py

   # Production
   ./run.sh
   ```

## Usage

1. Access the web interface at `http://localhost:5001`
2. Upload two PDF documents
3. Adjust text/handwriting weight using the slider
4. Click "Compare PDFs"
5. View results including:
   - Overall similarity score
   - Semantic flow analysis
   - Writing style variations
   - Text consistency checks
6. Download detailed report

## Project Structure

```
/
├── app/
│ ├── similarity/ # Analysis modules
│ ├── utils/ # PDF processing
│ ├── static/ # Frontend assets
│ └── templates/ # HTML templates
├── uploads/ # Temporary storage
├── reports/ # Generated reports
└── config.py # Configuration
```

## API Testing

```bash
python test_apis.py
```
