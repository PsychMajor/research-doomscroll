# BERT NER Model Setup

## Overview

The query parser now uses a lightweight BERT-based Named Entity Recognition (NER) model for better accuracy in extracting names, institutions, years, and topics/keywords from search queries.

## Model Details

- **Model**: `dslim/bert-base-NER`
- **Size**: ~400MB (downloads automatically on first use)
- **Speed**: Fast on CPU, optimized for local inference
- **Accuracy**: Significantly better than spaCy for person and organization detection

## Installation

```bash
# Install transformers library
pip install transformers torch

# The model will download automatically on first use
```

## How It Works

1. **BERT NER Model**: Uses a pre-trained BERT model fine-tuned for NER
   - Detects: PER (person), ORG (organization), LOC (location), MISC (miscellaneous)
   - More accurate than spaCy, especially for:
     - Lowercase names
     - Multiple authors
     - Complex name formats
     - Institution names

2. **Fallback Chain**:
   - First tries BERT NER (best accuracy)
   - Falls back to spaCy if transformers not available
   - Falls back to regex parser if no AI models available

## Performance

- **Memory**: ~500MB additional RAM when loaded
- **Speed**: ~50-100ms per query on CPU (first query slower due to model loading)
- **Accuracy**: Much better than spaCy for entity detection

## Usage

The parser automatically uses BERT if available. No code changes needed - just install transformers:

```bash
pip install transformers torch
```

The model will download and cache automatically on first use.

