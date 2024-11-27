import tiktoken
from PyPDF2 import PdfReader
import re
import argparse

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        reader = PdfReader(pdf_path)
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text())
        return pages
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def clean_text(text):
    """
    Clean and preprocess the text.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Cleaned text
    """
    if text is None:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def count_tokens(text, model="cl100k_base"):
    """
    Count tokens in the text using tiktoken.
    
    Args:
        text (str): Input text
        model (str): Model encoding to use (default: cl100k_base for text-embedding-ada-002)
        
    Returns:
        int: Number of tokens
    """
    try:
        encoding = tiktoken.get_encoding(model)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return 0

def count_words(text):
    """
    Count words in the text.
    
    Args:
        text (str): Input text
        
    Returns:
        int: Number of words
    """
    return len(text.split())

def analyze_pdf_tokens(pdf_path):
    """
    Analyze token count for a PDF file, including per-page analysis.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing token analysis
    """
    # Extract and clean text
    pages = extract_text_from_pdf(pdf_path)
    if pages is None:
        return None
    
    # Process each page
    cleaned_pages = [clean_text(page) for page in pages]
    page_tokens = [count_tokens(page) for page in cleaned_pages]
    page_words = [count_words(page) for page in cleaned_pages]
    
    total_tokens = sum(page_tokens)
    total_words = sum(page_words)
    
    return {
        "total_tokens": total_tokens,
        "total_words": total_words,
        "total_pages": len(pages),
        "tokens_per_page": page_tokens,
        "words_per_page": page_words,
        "average_tokens_per_page": total_tokens / len(pages) if pages else 0,
        "average_words_per_page": total_words / len(pages) if pages else 0,
        "text_length": sum(len(page) for page in cleaned_pages),
        "tokens_per_word": total_tokens / total_words if total_words else 0
    }

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Analyze token count in a PDF file')
    parser.add_argument('pdf_path', type=str, help='Path to the PDF file to analyze')
    parser.add_argument('--chunk-size', type=int, default=1000,
                        help='Number of characters per chunk for analysis (default: 1000)')
    
    args = parser.parse_args()
    
    # Use the provided arguments
    results = analyze_pdf_tokens(args.pdf_path)
    
    if results:
        print("\nPDF Token Analysis:")
        print(f"PDF File: {args.pdf_path}")
        print(f"Total Tokens: {results['total_tokens']}")
        print(f"Total Words: {results['total_words']}")
        print(f"Number of Pages: {results['total_pages']}")
        # print(f"Tokens per Page: {results['tokens_per_page']}")
        # print(f"Words per Page: {results['words_per_page']}")
        print(f"Average Tokens per Page: {results['average_tokens_per_page']:.2f}")
        print(f"Average Words per Page: {results['average_words_per_page']:.2f}")
        print(f"Text Length (characters): {results['text_length']}")
        # print(f"Tokens per Word: {results['tokens_per_word']:.2f}")
    else:
        print(f"Failed to analyze PDF file: {args.pdf_path}")