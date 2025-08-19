# GCP Workflow Samples

This repository contains sample Google Cloud Platform (GCP) workflow implementations demonstrating different event-driven processing patterns. The repository is organized into two main workflow examples:

## Workflow Examples

### 1. File Processing Workflow (`file-processing-workflow/`)
**Trigger**: GCS file upload → Eventarc → Cloud Workflows  
**Purpose**: Processes text files to count words, identify top frequent words, and store results in BigQuery  
**Components**: Cloud Functions + Cloud Workflows + BigQuery  

### 2. Pub/Sub Workflow (`pubsub-workflow/`)
**Trigger**: Pub/Sub message → Eventarc → Cloud Workflows  
**Purpose**: Processes JSON payloads to calculate file sizes and store results in GCS  
**Components**: Cloud Workflows only (no Cloud Functions)  

Both workflows demonstrate different GCP services and event-driven patterns:

## Repository Structure

```
gcp-workflow-sample/
│
├── file-processing-workflow/    # File processing workflow
│   ├── cf-word-count/           # Cloud Function for word counting
│   ├── cf-top-10-words/         # Cloud Function for top words
│   ├── cf-insert-bigquery/      # Cloud Function for BigQuery
│   ├── workflow.yaml            # Workflow definition
│   └── README.md                # Deployment instructions
│
├── pubsub-workflow/             # Pub/Sub triggered workflow
│   ├── pubsub.yaml              # Workflow definition
│   ├── sample-files/            # Test files
│   ├── payload.txt              # Example payload
│   └── README.md                # Deployment instructions
│
├── CLAUDE.md                    # Claude Code guidance
├── LICENSE
└── README.md                    # This overview file
```

## Getting Started

Each workflow has its own directory with detailed deployment instructions:

- **[File Processing Workflow](file-processing-workflow/README.md)**: Complete setup for GCS-triggered file processing with Cloud Functions and BigQuery
- **[Pub/Sub Workflow](pubsub-workflow/README.md)**: Setup for message-triggered file size analysis workflow

## Prerequisites

Both workflows require:

* A Google Cloud Project with billing enabled
* The `gcloud` CLI installed and authenticated
* Appropriate GCP APIs enabled (see individual workflow READMEs for specific requirements)

## Architecture Patterns

This repository demonstrates two common GCP event-driven patterns:

### When to Use Each Pattern

**File Processing Workflow** - Use when:
- Processing files uploaded to storage
- Need complex multi-step processing
- Building real-time message processing systems

**Pub/Sub Workflow** - Use when:
- Processing messages or events from multiple sources
- Want pure workflow orchestration
- Building batch message processing systems

Each pattern has different complexity and cost trade-offs - see individual workflow READMEs for detailed comparisons.