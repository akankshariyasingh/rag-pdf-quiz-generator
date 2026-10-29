
from pathlib import Path


def validate_pdf_upload(
    filename: str,
    file_bytes: bytes,
) -> tuple[bool, str]:
    """
    Validate an uploaded PDF using its filename and file signature.

    Returns:
        (is_valid, message)
    """
    if not filename or not filename.strip():
        return False, "Please provide a valid filename."

    if Path(filename).suffix.lower() != ".pdf":
        return False, "Only PDF files are supported."

    if not file_bytes:
        return False, "The uploaded file is empty."

    # Basic PDF signature check.
    if not file_bytes.startswith(b"%PDF-"):
        return False, "The file does not appear to be a valid PDF."

    return True, "PDF validation successful."


def format_file_size(size_bytes: int) -> str:
    """Convert a file size in bytes into a readable string."""
    if size_bytes < 0:
        return "Unknown size"

    if size_bytes < 1024:
        return f"{size_bytes} B"

    if size_bytes < 1024**2:
        return f"{size_bytes / 1024:.2f} KB"

    if size_bytes < 1024**3:
        return f"{size_bytes / (1024**2):.2f} MB"

    return f"{size_bytes / (1024**3):.2f} GB"


def sanitize_filename(filename: str) -> str:
    """Remove unsafe path components from an uploaded filename."""
    name = Path(filename).name.strip()

    # Replace characters that are inconvenient in stored filenames.
    safe_name = "".join(
        character
        if character.isalnum() or character in "._- "
        else "_"
        for character in name
    )

    safe_name = safe_name.strip(" .")

    if not safe_name:
        return "uploaded_document.pdf"

    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"

    return safe_name


def truncate_text(text: str, max_length: int = 200) -> str:
    """Shorten long text for display."""
    if max_length <= 0:
        return ""

    text = " ".join(text.split())

    if len(text) <= max_length:
        return text

    return text[: max_length - 3].rstrip() + "..."


def get_unique_filename(
    filename: str,
    existing_filenames: list[str],
) -> str:
    """
    Return a unique filename when a PDF with the same name exists.
    """
    safe_name = sanitize_filename(filename)
    existing = {name.lower() for name in existing_filenames}

    if safe_name.lower() not in existing:
        return safe_name

    path = Path(safe_name)
    counter = 2

    while True:
        candidate = f"{path.stem}_{counter}{path.suffix}"

        if candidate.lower() not in existing:
            return candidate

        counter += 1
