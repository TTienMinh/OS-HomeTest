import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv, set_key

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = "scraped_articles"
VECTOR_STORE_NAME = "OptiBot-Knowledge-Base"


def create_vector_store(vector_store_name: str = VECTOR_STORE_NAME):
    """
    Create a vector store
    """
    if os.getenv("VECTOR_STORE_ID"):
        print("Vector store already exists with ID:", os.getenv("VECTOR_STORE_ID"))
        return os.getenv("VECTOR_STORE_ID")

    vector_store = client.vector_stores.create(name=vector_store_name)
    print("Vector Store ID:", vector_store.id)
    set_key(".env", "VECTOR_STORE_ID", vector_store.id)
    return vector_store.id


def upload_file_to_vector_store(vector_store_id: str, file_paths: list):
    """
    Upload file to vector store
    """
    if not file_paths:
        print("No files found to upload.")
        return {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'status': 'skipped'
        }

    file_streams = []

    for file_path in file_paths:
        if os.path.exists(file_path):
            file_streams.append(open(file_path, "rb"))
        else:
            print(f"Skipping {file_path}, not a file.")
    
    if not file_streams:
        print("No valid files to upload.")
        return {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'status': 'no_valid_files'
        }

    try:
        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            files=file_streams
        )
        print(f"Upload status: {file_batch.status}")
        
        stats = {
            'total': file_batch.file_counts.total,
            'completed': file_batch.file_counts.completed,
            'failed': file_batch.file_counts.failed,
            'in_progress': file_batch.file_counts.in_progress,
            'cancelled': file_batch.file_counts.cancelled,
            'status': file_batch.status
        }

        print("File batch stats:", stats)
        return stats
    except Exception as e:
        print(f"Failed to add files to vector store {vector_store_id}: {e}")
        return {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'in_progress': 0,
            'cancelled': 0,
            'status': 'failed'
        }


def run_vector_store_setup(file_paths: list):
    """
    Run the complete vector store setup
    """
    vector_store_id = create_vector_store()
    vector_store_batches = upload_file_to_vector_store(
        vector_store_id=vector_store_id,
        file_paths=file_paths
    )
    return vector_store_batches


if __name__ == "__main__":
    run_vector_store_setup([os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".md")])