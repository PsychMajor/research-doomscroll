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
        H2O -> H<sub>2</sub>O
    
    Args:
        text: Input text with scientific notation
        
    Returns:
        Formatted HTML string or None
    """
    if not text:
        return text
    
    # Convert superscripts first (e.g., 10^6, x^2)
    # Pattern: ^digit or ^{digits}
    text = re.sub(r'\^(\d+)', r'<sup>\1</sup>', text)
    text = re.sub(r'\^\{([^}]+)\}', r'<sup>\1</sup>', text)
    
    # Convert subscripts more carefully - only for:
    # 1. Greek letters followed by digits (β2, α1, etc.)
    # 2. Chemical formulas: single uppercase letter + 1-2 digits + uppercase letter (H2O, CO2)
    # 3. Chemical formulas: single uppercase letter + 1-2 digits + end of word (N2, O2)
    
    # Greek letters with digits (β2, α1, γ3, etc.)
    text = re.sub(r'([α-ωΑ-Ω])(\d+)', r'\1<sub>\2</sub>', text)
    
    # Chemical formulas: Handle common patterns:
    # 1. Letter(s) + digits + letter (H2O, N2O) - digits in middle
    # 2. Letter(s) + digits at end (CO2, N2, O2) - digits at end
    # 
    # This matches: H2O, CO2, N2, O2, N2O, etc.
    # Does NOT match: Gpr85, GPCR, cell2, etc. (longer words with mixed case)
    
    # Pattern 1: One or more uppercase letters + digits + uppercase letter (H2O, N2O)
    # This handles formulas where digits are in the middle
    text = re.sub(r'\b([A-Z]+)(\d{1,2})([A-Z])', r'\1<sub>\2</sub>\3', text)
    
    # Pattern 2: One or more uppercase letters + digits at end of word
    # But only if the word is short (2-4 chars total) to avoid matching gene names
    # This handles: CO2, N2, O2 (short chemical formulas)
    # Does NOT handle: Gpr85 (too long), GPCR85 (too long)
    text = re.sub(r'\b([A-Z]{1,2})(\d{1,2})\b(?![a-z])', r'\1<sub>\2</sub>', text)
    
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
