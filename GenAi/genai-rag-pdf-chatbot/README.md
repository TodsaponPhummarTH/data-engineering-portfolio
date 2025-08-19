# GenAI PDF Chatbot using RAG (Retrieval-Augmented Generation)

This project builds a local GenAI chatbot that can read PDF documents (like books or study guides), convert them to embeddings using HuggingFace models, store them in a FAISS vector DB, and chat with you over the content using LangChain.

## Features
- Local processing
- HuggingFace embeddings
- FAISS vector store
- LangChain-powered chat

## Requirements
- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/genai-rag-pdf-chatbot.git
   cd genai-rag-pdf-chatbot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Alternatively, you can install dependencies manually:
   ```bash
   pip install langchain faiss-cpu PyPDF2 transformers sentence-transformers
   ```

## Usage

1. Place your PDF files in the `data/` folder.
2. Run the chatbot:
   ```bash
   python main.py
   ```
3. Start chatting with the bot about the content of your PDFs!

## Contributing

Contributions are welcome! If you have suggestions or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Made for learning & portfolio purposes 🚀
