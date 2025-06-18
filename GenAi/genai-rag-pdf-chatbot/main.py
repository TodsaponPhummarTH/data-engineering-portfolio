"""
Main Application Module
======================

This module contains the main application logic for the RAG PDF Chatbot.
It demonstrates the complete workflow from PDF loading to vector storage.
"""

import logging
from pathlib import Path
from src.pdf_loader import PDFLoader
from src.text_splitter import TextSplitter
from src.embedder import Embedder
from src.vector_store import VectorStore
from src.config import config
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from pydantic import BaseModel

# Initialize logger
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
pdf_loader = PDFLoader()
text_splitter = TextSplitter(
    chunk_size=config.text_processing.chunk_size,
    overlap=config.text_processing.chunk_overlap
)
embedder = Embedder(model_name=config.embedding.model_name)
vector_store = VectorStore()

@app.get("/")
async def home():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Clear existing files in data directory
        data_dir = Path("data")
        if data_dir.exists():
            for item in data_dir.glob("*"):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    import shutil
                    shutil.rmtree(item)
        
        # Save uploaded file
        file_path = Path("data") / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file is a PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            
        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        # Process the PDF immediately
        pdf_loader = PDFLoader(str(file_path))
        pdf_loader.load_document()
        text = pdf_loader.extract_text()
        
        # Log for debugging
        logger.info(f"Extracted text length: {len(text)}")
        logger.info(f"First 100 characters: {text[:100]}")
        
        # Calculate stats before processing
        text_length = len(text)
        chunks = text_splitter.split_by_sentences(text)
        chunks_count = len(chunks)
        
        # Generate embeddings and save to vector store
        embeddings = embedder.batch_embed(chunks)
        vector_store.save(embeddings, chunks)
        
        return {
            "success": True,
            "filename": file.filename,
            "message": "File uploaded and processed successfully",
            "stats": {
                "text_length": text_length,
                "chunks_count": chunks_count
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        context = vector_store.get_context_for_query(request.query)
        return {
            "response": context,
            "sources": [f"Chunk {i}" for i in range(len(context.split('\n')))]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """
    Main application entry point
    """
    try:
        # Initialize components
        logger.info("Initializing components...")
        text_splitter = TextSplitter(
            chunk_size=config.text_processing.chunk_size,
            overlap=config.text_processing.chunk_overlap
        )
        embedder = Embedder(model_name=config.embedding.model_name)
        vector_store = VectorStore()
        
        logger.info("Application initialized successfully")
        
    except Exception as e:
        logger.error(f"Error in main application: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Error in main application: {str(e)}")
        raise

if __name__ == "__main__":
    main()