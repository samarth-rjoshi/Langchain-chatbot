# LangChain Documentation Chatbot

A sophisticated chatbot application built using LangChain and Streamlit that provides intelligent responses to queries about LangChain and Haystack frameworks. The chatbot uses advanced language models and vector stores to deliver accurate and context-aware answers.

## Features

- 🤖 Interactive chatbot interface using Streamlit
- 📚 Support for both LangChain and Haystack documentation
- 🔍 Vector search using Qdrant for efficient document retrieval
- 🎯 Context-aware responses using Mistral-7B model
- 💾 Persistent chat history
- 🎨 Beautiful and responsive UI

## Project Structure

```
├── app.py              # Main Streamlit application
├── c.py               # Alternative implementation with custom styling
├── combined.py        # Combined LangChain and Haystack implementation
├── components.py      # UI components and utilities
├── pdf.py            # PDF processing utilities
├── requirements.txt   # Project dependencies
└── data/             # Documentation data directory
    ├── Langchain/
    ├── Langserve/
    ├── Langsmith/
    └── paper/
```

## Prerequisites

- Python 3.11+
- Pip package manager
- HuggingFace API token
- Qdrant cloud account and API keys

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd langchain-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add your API keys:
```env
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

## Running the Application

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Alternative implementations:
```bash
streamlit run c.py         # Run the custom-styled version
streamlit run combined.py  # Run the combined LangChain-Haystack version
```

## Features in Detail

### Vector Store Integration
- Uses Qdrant as a vector store for efficient document retrieval
- Supports multiple collections for different documentation sources
- Implements semantic search for accurate document matching

### Language Model
- Integrates with Mistral-7B-Instruct model through HuggingFace
- Configured for optimal response generation
- Customizable temperature and token settings

### User Interface
- Clean and modern design with custom CSS styling
- Responsive chat interface
- Support for code syntax highlighting
- Easy-to-use document source selection

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LangChain team for the excellent framework
- Haystack team for their contribution to NLP
- Streamlit team for the amazing web framework
- HuggingFace for providing access to state-of-the-art language models
- Qdrant team for their vector database solution
