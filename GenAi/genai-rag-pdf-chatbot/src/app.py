from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from pathlib import Path
from src.vector_store import VectorStore
from src.text_splitter import TextSplitter
from src.config import config
from src.pdf_loader import PDFLoader
from src.embedder import Embedder
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize vector store and text splitter
vector_store = VectorStore()
text_splitter = TextSplitter(
    chunk_size=config.chunk_size,
    overlap=config.chunk_overlap
)

@app.get("/")
async def home():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_path = Path("data") / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        # Process the file
        pdf_loader = PDFLoader(str(file_path))
        text = pdf_loader.extract_text()
        chunks = text_splitter.split_by_sentences(text)
        embedder = Embedder(model_name=config.model_name)
        embeddings = embedder.batch_embed(chunks)

        # Save to vector store
        vector_store.save(embeddings, chunks)
        
        return {"message": "File processed successfully", "filename": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat request model
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