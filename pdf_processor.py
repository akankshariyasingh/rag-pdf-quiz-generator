
import fitz  # PyMuPDF

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_pdf(pdf_bytes: bytes) -> list[dict]:
    """
    Extract text from a PDF.

    Args:
        pdf_bytes: PDF file content as bytes.

    Returns:
        A list of dictionaries containing page numbers and text.
    """
    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")

    pages = []

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
            if len(pdf) == 0:
                raise ValueError("The PDF contains no pages.")

            for page_index, page in enumerate(pdf):
                text = page.get_text("text").strip()

                if text:
                    pages.append(
                        {
                            "page_number": page_index + 1,
                            "text": text,
                        }
                    )

    except Exception as exc:
        if isinstance(exc, ValueError):
            raise

        raise ValueError(
            "Could not read the PDF. Please upload a valid PDF file."
        ) from exc

    if not pages:
        raise ValueError(
            "No readable text was found in this PDF. "
            "It may be a scanned PDF that needs OCR."
        )

    return pages


def split_text_into_chunks(
    pages: list[dict],
    source_name: str,
) -> list[dict]:
    """
    Split extracted page text into overlapping chunks.

    Each chunk retains its source filename and page number.
    """
    if not pages:
        return []

    if CHUNK_SIZE <= 0:
        raise ValueError("CHUNK_SIZE must be greater than zero.")

    if not 0 <= CHUNK_OVERLAP < CHUNK_SIZE:
        raise ValueError(
            "CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = []

    for page in pages:
        page_text = page["text"]

        page_chunks = splitter.split_text(page_text)

        for chunk_index, chunk_text in enumerate(page_chunks):
            if not chunk_text.strip():
                continue

            chunks.append(
                {
                    "text": chunk_text.strip(),
                    "source": source_name,
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                }
            )

    return chunks


def process_pdf(
    pdf_bytes: bytes,
    source_name: str,
) -> list[dict]:
    """
    Complete PDF pipeline: extract text and split it into chunks.
    """
    pages = extract_text_from_pdf(pdf_bytes)

    chunks = split_text_into_chunks(
        pages=pages,
        source_name=source_name,
    )

    if not chunks:
        raise ValueError("No text chunks could be created from this PDF.")

    return chunks

