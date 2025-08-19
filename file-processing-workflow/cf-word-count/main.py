# This Cloud Function counts the total number of words in a text file.

import os
from google.cloud import storage

# Initialize Google Cloud Storage client
storage_client = storage.Client()

def count_words(request):
  """
  HTTP Cloud Function to count total words in a text file from GCS.
  Expects JSON payload with 'bucket_name' and 'file_path'.
  """
  request_json = request.get_json(silent=True)
  if not request_json:
    return {'error': 'Invalid JSON'}, 400

  bucket_name = request_json.get('bucket_name')
  file_path = request_json.get('file_path')

  if not bucket_name or not file_path:
    return {'error': 'Missing bucket_name or file_path'}, 400

  print(f"Counting words for gs://{bucket_name}/{file_path}")

  try:
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    contents = blob.download_as_text()

    # Simple word count: split by whitespace
    words = contents.split()
    total_words = len(words)

    print(f"Total words in {file_path}: {total_words}")
    return {'total_words': total_words}

  except Exception as e:
    print(f"Error counting words for {file_path}: {e}")
    return {'error': str(e)}, 500
