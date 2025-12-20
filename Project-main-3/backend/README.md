# GroupMeet Backend

Flask backend application for GroupMeet study group matching platform.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (see main README.md)

4. Run development server:
```bash
python app.py
```

## Project Structure

- `app.py` - Flask application factory
- `config.py` - Configuration management
- `auth/` - CAS authentication module
- `api/` - REST API routes
- `src/qc/` - Quality control module
- `src/aggregation/` - Matching algorithm
- `src/services/` - Shared services
- `models/` - Data models
- `utils/` - Utility functions

## Testing

Run tests with pytest:
```bash
pytest tests/
```

