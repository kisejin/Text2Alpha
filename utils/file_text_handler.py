import os


def get_code_from_text(text):
    """Extracts the Python code segment from the provided text."""
    code_segment = text
    if "```" in text:
        code_segment = code_segment.split("```")[1]
    if "python" in text:
        code_segment = code_segment[code_segment.find("python") + 6 :]
    return code_segment.strip()


def load_file(FILE_PATH: str):
    """Loads content of file."""
    with open(FILE_PATH, "r") as f:
        contents = "".join(f.readlines())
    return contents


def save_file(FILE_PATH: str, content: str):
    """Saves content to file."""
    with open(FILE_PATH, "w") as f:
        f.write(content)
