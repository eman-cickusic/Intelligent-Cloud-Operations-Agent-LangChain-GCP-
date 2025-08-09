import os
import json
import datetime
import requests # For triggering HTTP Cloud Function
from google.cloud import firestore, logging, bigquery, storage, monitoring_v3
from google.oauth2 import service_account
from google.api_python_client import discovery
# --- GCP Authentication & Client Initialization ---
# For local dev, set GOOGLE_APPLICATION_CREDENTIALS. In GCP, it's automatic.
def get_gcp_credentials():
   credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
   if credentials_path:
       return service_account.Credentials.from_service_account_file(credentials_path)
   return None
CREDENTIALS = get_gcp_credentials()
PROJECT_ID = CREDENTIALS.project_id if CREDENTIALS else os.getenv("GCP_PROJECT")
# Initialize all clients
db = firestore.Client(project=PROJECT_ID, credentials=CREDENTIALS)
logging_client = logging.LoggingClient(project=PROJECT_ID, credentials=CREDENTIALS)
bigquery_client = bigquery.Client(project=PROJECT_ID, credentials=CREDENTIALS)
storage_client = storage.Client(project=PROJECT_ID, credentials=CREDENTIALS)
monitoring_client = monitoring_v3.MetricServiceClient(credentials=CREDENTIALS)
# --- Firestore Functions ---
def add_task_to_firestore(task_description: str) -> str:
   """Adds a task to Firestore. Input: a string describing the task."""
   try:
       doc_ref = db.collection("tasks").add({"description": task_description, "status": "pending"})
       return f"Successfully added task with ID: {doc_ref[1].id}"
   except Exception as e:
       return f"Error adding task to Firestore: {e}"
# --- Cloud Logging & BigQuery ---
def query_gcp_logs(filter_query: str) -> str:
   """Queries GCP logs. Input: a valid GCP logging filter string."""
   try:
       entries = list(logging_client.list_entries(filter_=filter_query, page_size=5))
       log_list = [entry.payload for entry in entries]
       return json.dumps(log_list, indent=2) if log_list else "No logs found."
   except Exception as e:
       return f"Error querying GCP logs: {e}"
def execute_bigquery_query(query: str) -> str:
   """Executes a SQL query on BigQuery. Input: a valid SQL query string."""
   try:
       results = bigquery_client.query(query).result()
       rows = [dict(row) for row in results]
       return json.dumps(rows, indent=2, default=str) if rows else "Query returned no results."
   except Exception as e:
       return f"Error executing BigQuery query: {e}"
# --- NEW: Cloud Monitoring Function ---
def query_gcp_metrics(metric_filter: str) -> str:
   """
   Queries GCP Monitoring for a specific metric.
   Example Input: 'metric.type = "compute.googleapis.com/instance/cpu/utilization"'
   """
   try:
       interval = monitoring_v3.TimeInterval(
           {
               "end_time": datetime.datetime.now(datetime.timezone.utc),
               "start_time": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10),
           }
       )
       results = monitoring_client.list_time_series(
           request={
               "name": f"projects/{PROJECT_ID}",
               "filter": metric_filter,
               "interval": interval,
               "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
           }
       )
       output = [
           {
               "resource": series.resource.labels,
               "points": [{"value": point.value.double_value, "time": point.interval.end_time.isoformat()} for point in series.points],
           }
           for series in results
       ]
       return json.dumps(output, indent=2) if output else "No metric data found."
   except Exception as e:
       return f"Error querying GCP metrics: {e}"
# --- NEW: Terraform State Reader Function ---
def query_terraform_state(bucket_and_resource_type: str) -> str:
   """
   Reads a Terraform state file from GCS and lists resources of a given type.
   Input should be a string like: 'your-tf-state-bucket-name/google_compute_instance'
   """
   try:
       bucket_name, resource_type = bucket_and_resource_type.split('/', 1)
       blob = storage_client.bucket(bucket_name).blob("terraform.tfstate")
       state_data = json.loads(blob.download_as_string())
       resources = [
           res["instances"][0]["attributes"]
           for res in state_data.get("resources", [])
           if res.get("type") == resource_type
       ]
       return json.dumps(resources, indent=2) if resources else f"No resources of type '{resource_type}' found."
   except Exception as e:
       return f"Error reading Terraform state from GCS: {e}. Ensure the bucket and file exist."
# --- NEW: Cloud Function Trigger ---
def trigger_cloud_function(function_url_and_data: str) -> str:
   """
   Triggers an HTTP-based Cloud Function.
   Input should be a string like: 'https://your-cloud-function-url {"key": "value"}'
   """
   try:
       url, data_str = function_url_and_data.split(' ', 1)
       data = json.loads(data_str)
       # For authenticated functions, you'd add an Authorization header here.
       # For simplicity, this assumes a public (unauthenticated) function.
       response = requests.post(url, json=data)
       response.raise_for_status() # Raise an exception for bad status codes
       return f"Successfully triggered Cloud Function. Response: {response.text}"
   except Exception as e:
       return f"Error triggering Cloud Function: {e}"