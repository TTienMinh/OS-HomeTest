import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = "scraped_articles"
VECTOR_STORE_NAME = "OptiBot-Knowledge-Base"


def upload_file(directory_path: str = DATA_DIR):
    """
    Upload files to OpenAI.
    """
    path_obj = Path(directory_path)

    if not path_obj.exists() or not path_obj.is_dir():
        print(f"Error: {directory_path} is not a valid directory.")
        return

    files_id = {}
    for file in path_obj.iterdir():
        try:
            response = client.files.create(
                file=file.open("rb"),
                purpose='assistants'
            )
            files_id[file.name] = response.id
            print(f"Successfully uploaded {file.name}. ID: {response.id}")
        except Exception as e:
            print(f"Failed to upload {file.name}: {e}")

    return files_id


def create_vector_store(vector_store_name: str = VECTOR_STORE_NAME):
    """
    Create a vector store
    """
    vector_store = client.vector_stores.create(name=vector_store_name)
    print("Vector Store ID:", vector_store.id)
    return vector_store


def upload_file_to_vector_store(file_id, vector_store_id, files_path: str = DATA_DIR):
    """
    Upload file to vector store
    """
    try:
        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            file_ids=file_id,
            files=[file.open("rb") for file in Path(files_path).iterdir()]
        )
        print(f"Upload status: {file_batch.status}")
        print(f"File counts: {file_batch.file_counts}")
        print(f"Total files: {file_batch.file_counts.total}")
        print(f"Completed: {file_batch.file_counts.completed}")
    except Exception as e:
        print(f"Failed to add files to vector store {vector_store_id.id}: {e}")
    
    return file_batch


def run_vector_store_setup():
    """
    Run the complete vector store setup
    """
    file_ids = upload_file()
    vector_store = create_vector_store()
    vector_store_batches = upload_file_to_vector_store(
        file_id=list(file_ids.values()),
        vector_store_id=vector_store.id
    )
    return vector_store_batches


if __name__ == "__main__":
    run_vector_store_setup()