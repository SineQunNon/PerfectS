# PerfectS

## Environment Setup

### Prerequisites
- Python 3.10.12

### Virtual Environment Setup
1. Create a virtual environment
```bash
python -m venv venv
```

2. Activate the virtual environment

On macOS and Linux:
```bash
source venv/bin/activate
```

### Install Dependencies
Install required packages using pip:
```bash
pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file in the root directory and add:
```
PYTHONPATH=
OPENAI_API_KEY=
PDF_PATH=
PPTX_PATH=
LOG_PATH=
```

## Project Structure
```
project/
├── templates/
│   └── pptx_template/
├── nltk.py
├── monitor.py
└── .env
```

## Running the Application
1. Run NLTK script:
```bash
python nltk.py
```

2. Run monitoring script:
```bash
python monitor.py
```
