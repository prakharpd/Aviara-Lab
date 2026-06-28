"""
ASE Lead Qualification Pipeline — Entry Point
Run: python main.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from utils.csv_helpers import init_csv
from utils.logger import log
import uvicorn

if __name__ == "__main__":
    init_csv()
    log("ASE Pipeline starting on http://localhost:8000")
    print("\n" + "="*40)
    print("   ASE LEAD QUALIFICATION PIPELINE")
    print("="*40)
    print("FastAPI server : http://localhost:8000")
    print("Streamlit dash : streamlit run dashboard.py")
    print("Test script    : python scripts/test_webhook.py")
    print("Webhook docs   : http://localhost:8000/docs")
    print("="*40 + "\n")
    uvicorn.run("routes.app:app", host="127.0.0.1", port=8000, reload=False)
