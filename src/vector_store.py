import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = "scraped_articles"
# VECTOR_STORE_NAME = "OptiBot-Knowledge-Base"


def upload_file(directory_path: str = DATA_DIR):
    """
    Upload files to OpenAI.
    """
    path_obj = Path(directory_path)

    if not path_obj.exists() or not path_obj.is_dir():
        print(f"Error: {directory_path} is not a valid directory.")
        return

    for file in path_obj.iterdir():
        try:
            response = client.files.create(
                file=file.open("rb"),
                purpose='assistants'
            )
            print(f"Successfully uploaded {file.name}. ID: {response.id}")
        except Exception as e:
            print(f"Failed to upload {file.name}: {e}")




if __name__ == "__main__":
    upload_file()
