# GCP File Processing Workflow

This repository contains the necessary code and configuration to set up an automated file processing pipeline on Google Cloud Platform (GCP). The pipeline is triggered when a file is uploaded to a Google Cloud Storage (GCS) bucket, processes the file to extract metadata, count words, identify top frequent words, and finally stores all this information in a BigQuery table.

## Architecture Overview

The solution leverages the following GCP services:

* **Google Cloud Storage (GCS):** Stores the input files and triggers the workflow upon new uploads.
* **Cloud Functions:**
    * `cloud-function-gcs-trigger`: A GCS-triggered function that initiates the Cloud Workflow.
    * `word-count-function`: An HTTP-triggered function that counts the total words in a text file.
    * `top-10-words-function`: An HTTP-triggered function that identifies the top 10 most frequent words.
    * `insert-bigquery-function`: An HTTP-triggered function that inserts the processed data into BigQuery.
* **Cloud Workflows:** Orchestrates the sequence of calls to the Cloud Functions and handles the extraction of GCS object metadata.
* **BigQuery:** Stores the structured output data from the file processing.

## Repository Structure

```
gcp-file-processor/
├── cf-gcs-trigger/         # Cloud Function to trigger the workflow
│   ├── main.py
│   └── requirements.txt
├── cf-word-count/          # Cloud Function for total word counting
│   ├── main.py
│   └── requirements.txt
├── cf-top-10-words/        # Cloud Function for top 10 word frequency
│   ├── main.py
│   └── requirements.txt
├── cf-insert-bigquery/     # Cloud Function for BigQuery insertion
│   ├── main.py
│   └── requirements.txt
├── workflow.yaml           # Cloud Workflow definition
└── README.md               # This file
```

## Prerequisites

Before deploying, ensure you have:

* A Google Cloud Project with billing enabled.
* The `gcloud` CLI installed and authenticated.
* Enabled the following GCP APIs in your project:
    * Cloud Functions API
    * Cloud Workflows API
    * Cloud Storage API
    * BigQuery API

## Deployment Steps

Follow these steps to deploy your GCP file processing workflow. Replace placeholder values like
```
export PROJECT_ID=<YOUR_GCP_PROJECT_ID>
export BUCKET_NAME=<YOUR_GCS_BUCKET_NAME>
export REGION="us-central1"
```

### 1. Set your GCP Project ID
```bash
gcloud config set project $PROJECT_ID
```

### 2. Create BigQuery Dataset and Table
First, set up your BigQuery table where the processed file information will be stored.
```bash
# Create a BigQuery Dataset
bq mk --dataset YOUR_GCP_PROJECT_ID:file_processing_dataset
```

You can execute this SQL in the BigQuery console or using the bq query command.
```
CREATE TABLE `$PROJECT_ID.file_processing_dataset.file_processing_results` (
    filename STRING,
    bucket STRING,
    size_bytes INTEGER,
    upload_date TIMESTAMP,
    total_words INTEGER,
    top_10_words JSON
);
```

### 3. Create a GCS Bucket
This is the bucket where files will be uploaded to trigger the workflow.
```
gsutil mb -l $REGION gs://$BUCKET_NAME
```

### 4. Deploy Cloud Functions

Navigate into the gcp-file-processor directory on your local machine.

Each Cloud Function requires its own requirements.txt file as specified in the repository structure section above.

#### A. cloud-function-gcs-trigger (GCS Trigger):
```
gcloud functions deploy cloud-function-gcs-trigger \
--runtime python39 \
--entry-point trigger_workflow \
--source cf-gcs-trigger/ \
--trigger-bucket $BUCKET_NAME \
--region $REGION \
--service-account "projects/$PROJECT_ID/serviceAccounts/cloud-function-gcs-trigger@$PROJECT_ID.iam.gserviceaccount.com" \
--memory 256MB \
--timeout 60s
```
Required IAM Permissions for cloud-function-gcs-trigger service account:
* Cloud Functions Invoker (auto-assigned)
* Workflows Invoker
* Service Account User (on the Workflow's runtime service account: file-processing-workflow-sa)

#### B. word-count-function:
```
gcloud functions deploy word-count-function \
--runtime python39 \
--entry-point count_words \
--source cf-word-count/ \
--trigger-http \
--region $REGION \
--service-account "projects/$PROJECT_ID/serviceAccounts/word-count-function@$PROJECT_ID.iam.gserviceaccount.com" \
--memory 256MB \
--timeout 60s \
--no-allow-unauthenticated # Only allow authenticated calls (from Workflow)
```
Required IAM Permissions for word-count-function service account:
* Cloud Storage Object Viewer

#### C. top-10-words-function:
```
gcloud functions deploy top-10-words-function \
--runtime python39 \
--entry-point get_top_10_words \
--source cf-top-10-words/ \
--trigger-http \
--region $REGION \
--service-account "projects/$PROJECT_ID/serviceAccounts/top-10-words-function@$PROJECT_ID.iam.gserviceaccount.com" \
--memory 256MB \
--timeout 60s \
--no-allow-unauthenticated
```
Required IAM Permissions for top-10-words-function service account:
* Cloud Storage Object Viewer

#### D. insert-bigquery-function:
```
gcloud functions deploy insert-bigquery-function \
--runtime python39 \
--entry-point insert_data_to_bigquery \
--source cf-insert-bigquery/ \
--trigger-http \
--region $REGION \
--service-account "projects/$PROJECT_ID/serviceAccounts/insert-bigquery-function@$PROJECT_ID.iam.gserviceaccount.com" \
--memory 256MB \
--timeout 60s \
--no-allow-unauthenticated
```
Required IAM Permissions for insert-bigquery-function service account:
* BigQuery Data Editor

### 5. Deploy the Cloud Workflow
__Important__: Before deploying, update the Cloud Function URLs in workflow.yaml with the actual URLs of your deployed functions. These URLs will be in the format `https://${REGION}-${PROJECT_ID}.cloudfunctions.net/FUNCTION_NAME`.

```
gcloud workflows deploy file-processing-workflow \
--source=workflow.yaml \
--location=$REGION \
--service-account "projects/$PROJECT_ID/serviceAccounts/file-processing-workflow-sa@Y$PROJECT_ID.iam.gserviceaccount.com"
```

Required IAM Permissions for file-processing-workflow-sa service account:
* Workflows Editor (for deployment)
* Workflows Invoker
* Cloud Functions Invoker (allows the workflow to call your HTTP Cloud Functions)
* Cloud Storage Object Viewer (allows the workflow to get GCS metadata directly)

Testing Your Workflow
Once all components are deployed, upload a text file (e.g., my_document.txt) to your YOUR_GCS_BUCKET_NAME GCS bucket.

```
echo "This is a sample document for testing the workflow. This document has multiple words for word counting. Sample words." > my_document.txt
gsutil cp my_document.txt gs://$BUCKET_NAME/my_document.txt
```

You can monitor the workflow executions in the Google Cloud Console:

__Cloud Functions Logs__: Navigate to Cloud Functions > cloud-function-gcs-trigger > Logs to see if the trigger fired.

__Workflow Executions__: Navigate to Cloud Workflows > file-processing-workflow > Executions to see the status and details of your workflow runs.

__BigQuery Table__: Check your $PROJECT_ID.file_processing_dataset.file_processing_results table in BigQuery to verify that new rows are inserted.

## Troubleshooting Tips
* Check Cloud Function Logs: If a workflow execution fails, check the logs for the specific Cloud Function that caused the failure.
* Check Workflow Execution Details: The workflow execution details in the Cloud Console will show which step failed and often provide error messages.
* IAM Permissions: The most common issue is incorrect IAM permissions. Double-check that all service accounts have the necessary roles assigned as specified above.
* Cloud Function URLs in Workflow: Ensure the URLs in workflow.yaml exactly match your deployed Cloud Function URLs.