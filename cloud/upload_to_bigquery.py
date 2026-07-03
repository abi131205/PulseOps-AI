import os
import glob
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
from dotenv import load_dotenv

# Load configurations
load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BIGQUERY_DATASET", "pulseops_ai")

def upload_csv_to_bigquery():
    if not PROJECT_ID:
        print("ERROR: GCP_PROJECT_ID not set in environment. Skipping BigQuery load.")
        print("Set GCP_PROJECT_ID in your .env file to enable analytical data warehouse uploads.")
        return

    print(f"Connecting to Google BigQuery (Project: {PROJECT_ID})...")
    client = bigquery.Client(project=PROJECT_ID)
    
    # Ensure dataset exists
    dataset_ref = client.dataset(DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} found.")
    except Exception:
        print(f"Dataset {DATASET_ID} not found. Creating dataset...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"Dataset {DATASET_ID} created successfully.")

    # Locate CSV files in datasets folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_files = glob.glob(os.path.join(base_dir, "datasets", "*.csv"))
    
    if not csv_files:
        print("No CSV files found to upload in datasets/ directory.")
        return

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        table_name = os.path.splitext(file_name)[0]
        table_ref = dataset_ref.table(table_name)
        
        print(f"Uploading {file_name} to BigQuery table {DATASET_ID}.{table_name}...")
        
        # Configure load job
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        
        try:
            with open(file_path, "rb") as source_file:
                load_job = client.load_table_from_file(
                    source_file, table_ref, job_config=job_config
                )
            load_job.result() # Wait for job to complete
            print(f"Successfully uploaded {table_name} table. Total rows loaded: {load_job.output_rows}")
        except GoogleAPIError as e:
            print(f"Failed to upload {table_name} due to BigQuery API error: {e}")
        except Exception as e:
            print(f"Error loading {file_name}: {e}")

if __name__ == "__main__":
    upload_csv_to_bigquery()
