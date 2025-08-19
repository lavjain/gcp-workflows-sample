# This Cloud Function counts the top 10 most frequent words in a text file.

import os
import re
from collections import Counter
from google.cloud import storage

# Initialize Google Cloud Storage client
storage_client = storage.Client()

def get_top_10_words(request):
  """
  HTTP Cloud Function to get top 10 words and their frequencies from a text file.
  Expects JSON payload with 'bucket_name' and 'file_path'.
  """
  request_json = request.get_json(silent=True)
  if not request_json:
    return {'error': 'Invalid JSON'}, 400

  bucket_name = request_json.get('bucket_name')
  file_path = request_json.get('file_path')

  if not bucket_name or not file_path:
    return {'error': 'Missing bucket_name or file_path'}, 400

  print(f"Getting top 10 words for gs://{bucket_name}/{file_path}")

  try:
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    contents = blob.download_as_text()

    # Normalize text: lowercase, remove punctuation, split into words
    # Use re.findall to extract words (alphanumeric sequences)
    words = re.findall(r'\b\w+\b', contents.lower())

    # Count word frequencies
    word_counts = Counter(words)

    # Get top 10 most common words
    top_10 = word_counts.most_common(10)

    # Format for JSON output
    top_10_list = [{'word': word, 'count': count} for word, count in top_10]

    print(f"Top 10 words in {file_path}: {top_10_list}")
    return {'top_10_words': top_10_list}

  except Exception as e:
    print(f"Error getting top 10 words for {file_path}: {e}")
    return {'error': str(e)}, 500
