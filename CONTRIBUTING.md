# Contributing to Email Productivity Agent

This project is a hiring challenge submission. However, suggestions and feedback are welcome!

## Code Structure

- `app.py` - Main Streamlit application
- `src/` - Core backend modules
  - `llm_client.py` - LLM integration
  - `prompt_manager.py` - Prompt template management
  - `email_processor.py` - Email processing pipeline
  - `draft_manager.py` - Draft generation
  - `email_agent.py` - Conversational agent
- `data/` - Data files and storage
- `test_components.py` - Component tests

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up `.env` file with API key
4. Run tests: `python test_components.py`
5. Start app: `streamlit run app.py`

## Code Standards

- Python 3.8+ compatible
- Type hints for function parameters
- Docstrings for all classes and functions
- Error handling for LLM calls
- JSON for data storage

## Testing

Run component tests before committing:
```bash
python test_components.py
```

## Questions?

Open an issue on GitHub or contact the maintainer.
