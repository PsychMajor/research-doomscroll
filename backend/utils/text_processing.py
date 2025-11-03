"""
Text processing utilities including scientific notation formatting
and text summarization
"""
import re
from typing import Optional
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer


def format_scientific_text(text: Optional[str]) -> Optional[str]:
    """
    Convert scientific notation to HTML with proper subscripts and superscripts
    
    Examples:
        β2 -> β<sub>2</sub>
        10^6 -> 10<sup>6</sup>
        CO2 -> CO<sub>2</sub>
    
    Args:
        text: Input text with scientific notation
        
    Returns:
        Formatted HTML string or None
    """
    if not text:
        return text
    
    # Convert subscripts (e.g., β2, H2O, CO2)
    # Pattern: letter followed by digit(s)
    text = re.sub(r'([A-Za-zα-ωΑ-Ω])(\d+)', r'\1<sub>\2</sub>', text)
    
    # Convert superscripts (e.g., 10^6, x^2)
    # Pattern: ^digit or ^{digits}
    text = re.sub(r'\^(\d+)', r'<sup>\1</sup>', text)
    text = re.sub(r'\^\{([^}]+)\}', r'<sup>\1</sup>', text)
    
    return text


def summarize_text(text: str, sentences_count: int = 2) -> Optional[str]:
    """
    Summarize text using LSA (Latent Semantic Analysis) algorithm
    
    Args:
        text: The text to summarize
        sentences_count: Number of sentences in the summary
    
    Returns:
        Summarized text string or None
    """
    if not text or len(text.strip()) < 50:
        return None
    
    try:
        # Parse the text
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        
        # Create LSA summarizer
        summarizer = LsaSummarizer()
        
        # Generate summary
        summary_sentences = summarizer(parser.document, sentences_count=sentences_count)
        
        # Join sentences into a single string
        summary = " ".join([str(sentence) for sentence in summary_sentences])
        
        return summary if summary else None
        
    except Exception as e:
        print(f"⚠️  Summarization error: {e}")
        # Fallback to first N characters
        if len(text) > 200:
            return text[:200].rsplit(" ", 1)[0] + "..."
        return None
