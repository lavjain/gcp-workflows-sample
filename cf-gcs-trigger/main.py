# This Cloud Function is triggered by GCS file uploads and invokes the Cloud Workflow.

import os
import json
from google.cloud import workflows_v1beta
from google.cloud.workflows_v1beta.services.workflows import WorkflowsClient
# The WorkflowsClient.execute_workflow method can accept parameters directly.

# Initialize the Workflows client
workflows_client = WorkflowsClient()

def trigger_workflow(event, context):
  """
  Triggers a Cloud Workflow when a new file is uploaded to GCS.

  Args:
      event (dict): Event payload containing GCS file information.
      context (google.cloud.functions.Context): Metadata for the event.
  """
  bucket_name = event['bucket']
  file_name = event['name']

  # Ensure the file is not a directory or empty
  if not file_name or file_name.endswith('/'):
    print(f"Skipping directory or empty file name: {file_name}")
    return

  project_id = os.environ.get('GCP_PROJECT') # Automatically set in Cloud Functions environment
  location = 'us-central1' # Or your desired workflow location
  workflow_name = 'file-processing-workflow' # The name of your Cloud Workflow

  # Construct the workflow path
  workflow_resource = workflows_client.workflow_path(
      project_id, location, workflow_name
  )

  # Prepare input arguments for the workflow
  # Workflows expects a JSON string for arguments
  input_args = json.dumps({
      "file_path": file_name,
      "bucket_name": bucket_name
  })

  print(f"Triggering workflow '{workflow_name}' for file gs://{bucket_name}/{file_name}")

  try:
    # Execute the workflow by passing name and argument directly
    # Note: Your IDE might show an "Unresolved attribute reference" warning here.
    # This is typically an IDE/linter issue and not a runtime error,
    # as the method is available in google-cloud-workflows==1.18.2.
    response = workflows_client.execute_workflow(
        name=workflow_resource,
        argument=input_args
    )
    print(f"Workflow execution started: {response.name}")

  except Exception as e:
    print(f"Error triggering workflow: {e}")
    raise
