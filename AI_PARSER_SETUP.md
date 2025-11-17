# AI Query Parser Setup

The query parser now uses **spaCy**, a lightweight NLP library that runs entirely on local CPU (no GPU needed, no external API calls).

## Installation

### Option 1: Quick Setup (Recommended)

```bash
# Install spaCy
pip install spacy

# Download the small English model (~12MB)
python -m spacy download en_core_web_sm
```

### Option 2: Add to requirements.txt

If you have a `requirements.txt` file, add:

```
spacy>=3.7.0
```

Then run:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## How It Works

### **AI-Powered Parsing**
- Uses **Named Entity Recognition (NER)** to identify person names (authors)
- Automatically detects author names like "John Smith", "Michael J. Iadarola"
- Handles various query formats intelligently

### **Lightweight & Fast**
- **Model size**: ~12MB (en_core_web_sm)
- **Speed**: Processes queries in milliseconds
- **CPU-only**: No GPU required
- **Local**: All processing happens on your machine, no API calls

### **Fallback Support**
- If spaCy is not installed, automatically falls back to the regex-based parser
- No breaking changes - the system works either way

## Performance

- **Memory**: ~50-100MB additional RAM
- **Speed**: <10ms per query on modern CPUs
- **Accuracy**: Significantly better than regex for complex queries

## Testing

The parser will automatically use spaCy if available, or fall back to regex parsing if not. Both methods work, but spaCy provides better accuracy for:
- Complex author names
- Queries with multiple authors
- Unusual name formats

## Example Queries

All of these work with the AI parser:

- `"machine learning by John Smith"`
- `"John Smith, Jane Doe neural networks"`
- `"pain research by Michael J. Iadarola"`
- `"by John Smith machine learning"`
- `"quantum computing papers"`

