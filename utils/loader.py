import fitz  # PyMuPDF


def load_and_chunk_pdf(pdf_path: str, chunk_size: int = 150, overlap: int = 30) -> list[str]:
    """
    Load a PDF and split the text into overlapping fixed-size word chunks.

    Args:
        pdf_path:   Path to the PDF file.
        chunk_size: Approximate number of words per chunk.
        overlap:    Number of words to repeat at the start of each new chunk
                    so context is not lost at boundaries.

    Returns:
        List of non-empty text chunk strings.
    """
    doc = fitz.open(pdf_path)

    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    doc.close()

    words = full_text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap
    i = 0
    while i < len(words):
        chunk = " ".join(words[i: i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())
        i += step

    return chunks
