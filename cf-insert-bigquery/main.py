# This Cloud Function inserts processed data into a BigQuery table.

import os
from google.cloud import bigquery
import json # To handle the JSON type for top_10_words

# Initialize BigQuery client
bigquery_client = bigquery.Client()

# Define your BigQuery dataset and table
DATASET_ID = 'file_processing_dataset'
TABLE_ID = 'file_processing_results'

def insert_data_to_bigquery(request):
  """
  HTTP Cloud Function to insert processed file data into BigQuery.
  Expects JSON payload with all file processing results.
  """
  request_json = request.get_json(silent=True)
  if not request_json:
    return {'error': 'Invalid JSON payload'}, 400

  # Extract data from the request payload
  filename = request_json.get('filename')
  bucket = request_json.get('bucket')
  size_bytes = request_json.get('size_bytes')
  upload_date = request_json.get('upload_date') # Should be ISO format string
  total_words = request_json.get('total_words')
  top_10_words_data = request_json.get('top_10_words')

  # Validate essential fields
  if not all([filename, bucket, size_bytes is not None, upload_date, total_words is not None, top_10_words_data is not None]):
    return {'error': 'Missing required fields in payload'}, 400

  print(f"Inserting data for file {filename} into BigQuery...")

  # Convert top_10_words_data to a JSON string if it's not already
  # BigQuery's JSON type will automatically handle JSON strings
  # if the source data is already a dict/list of dicts, it will be handled.
  # Otherwise, convert it to a string.
  try:
    if isinstance(top_10_words_data, (list, dict)):
      top_10_words_json_string = json.dumps(top_10_words_data)
    else:
      top_10_words_json_string = top_10_words_data # Assume it's already a string
  except TypeError as e:
    print(f"Warning: Could not serialize top_10_words_data to JSON string: {e}")
    top_10_words_json_string = str(top_10_words_data) # Fallback to string representation

  rows_to_insert = [
      {
          "filename": filename,
          "bucket": bucket,
          "size_bytes": size_bytes,
          "upload_date": upload_date,
          "total_words": total_words,
          "top_10_words": top_10_words_json_string # BigQuery JSON field expects a JSON string
      }
  ]

  try:
    table_ref = bigquery_client.dataset(DATASET_ID).table(TABLE_ID)
    errors = bigquery_client.insert_rows(table_ref, rows_to_insert)

    if errors:
      print(f"Encountered errors while inserting rows: {errors}")
      return {'status': 'error', 'errors': errors}, 500
    else:
      print(f"Successfully inserted data for {filename} into BigQuery.")
      return {'status': 'success'}

  except Exception as e:
    print(f"Error inserting into BigQuery: {e}")
    return {'error': str(e)}, 500
