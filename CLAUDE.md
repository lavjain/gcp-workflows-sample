# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains two Google Cloud Platform (GCP) workflow examples demonstrating different event-driven patterns:

1. **File Processing Workflow** (`file-processing-workflow/`): Triggered by file uploads to GCS via Eventarc. Processes text files to count words, identify top frequent words, and store results in BigQuery.
2. **Pub/Sub Workflow** (`pubsub-workflow/`): Triggered by Pub/Sub messages. Processes JSON payloads to calculate file sizes and store results in GCS.

## Architecture

### File Processing Workflow
- **Trigger**: GCS file upload → Eventarc → Cloud Workflows
- **Components**: 3 Cloud Functions (word count, top words, BigQuery insert) + Cloud Workflows orchestration
- **Data Flow**: GCS → Word Count → Top Words → BigQuery
- **Entry Point**: `file-processing-workflow/workflow.yaml:4` (main function)

### Pub/Sub Workflow 
- **Trigger**: Pub/Sub message → Eventarc → Cloud Workflows  
- **Components**: Cloud Workflows only (no Cloud Functions)
- **Data Flow**: Pub/Sub → GCS (read/write) → File size analysis
- **Entry Point**: `pubsub-workflow/pubsub.yaml`

## Code Structure

### Cloud Functions (Python) - File Processing Workflow
- **file-processing-workflow/cf-word-count/**: Counts total words in text files
  - Entry point: `count_words` function in `main.py:9`
  - Dependencies: `google-cloud-storage`
- **file-processing-workflow/cf-top-10-words/**: Finds most frequent words using Counter
  - Entry point: `get_top_10_words` function in `main.py:11`
  - Dependencies: `google-cloud-storage`
- **file-processing-workflow/cf-insert-bigquery/**: Inserts processed data to BigQuery
  - Entry point: `insert_data_to_bigquery` function in `main.py:13`
  - Dependencies: `google-cloud-bigquery`

### Cloud Workflows (YAML)
- **file-processing-workflow/workflow.yaml**: File processing orchestration
- **pubsub-workflow/pubsub.yaml**: Pub/Sub message processing

## Development Commands

### Testing Cloud Functions Locally
```bash
# No package.json - these are Python Cloud Functions
# Test functions using the Python standard library or pytest if added

# Install dependencies for each function:
cd file-processing-workflow/cf-word-count && pip install -r requirements.txt
cd file-processing-workflow/cf-top-10-words && pip install -r requirements.txt  
cd file-processing-workflow/cf-insert-bigquery && pip install -r requirements.txt
```

### Deployment Commands
```bash
# Deploy individual Cloud Functions (requires gcloud CLI)
cd file-processing-workflow
gcloud functions deploy word-count-function --runtime python310 --entry-point count_words --source cf-word-count/ --trigger-http

# Deploy Cloud Workflows  
gcloud workflows deploy file-processing-workflow --source=workflow.yaml --location=us-central1

# Deploy Pub/Sub workflow
cd ../pubsub-workflow
gcloud workflows deploy file-processing-pubsub-workflow --source=pubsub.yaml --location=us-central1
```

## Key Configuration

### Environment Variables
- `GOOGLE_CLOUD_PROJECT_ID`: Used in file-processing-workflow/workflow.yaml:12 for dynamic Cloud Function URLs
- Region: Hardcoded to "us-central1" in file-processing-workflow/workflow.yaml:13

### BigQuery Schema
```sql
CREATE TABLE file_processing_dataset.file_processing_results (
    filename STRING,
    bucket STRING, 
    size_bytes INTEGER,
    upload_date TIMESTAMP,
    total_words INTEGER,
    top_10_words JSON
);
```

## Important Notes

- Cloud Functions use HTTP triggers with OIDC authentication
- Workflows construct function URLs dynamically using project ID and region
- Word counting uses simple whitespace splitting
- Top words analysis normalizes text (lowercase, regex word extraction)
- BigQuery function handles JSON serialization for the top_10_words field
- Each workflow has its own README.md with detailed deployment instructions
- Both workflows require specific IAM permissions as detailed in their respective READMEs

## Repository Organization

- **file-processing-workflow/**: Self-contained GCS-triggered workflow with Cloud Functions
- **pubsub-workflow/**: Self-contained Pub/Sub-triggered workflow (workflows only)
- Each directory includes complete deployment instructions and examples
- Main README.md provides high-level overview of both patterns