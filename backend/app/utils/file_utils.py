import os
from uuid import uuid4


def save_uploaded_file(upload_dir: str, file) -> str:
    """
    Save uploaded file to disk and return file path
    """
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path
