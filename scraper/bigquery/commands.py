import click
from google.api_core.exceptions import Conflict
from google.cloud import bigquery
from google.oauth2 import service_account


def Client(key_path):
    if key_path is not None:
        credentials = service_account.Credentials.from_service_account_file(
            key_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        return bigquery.Client(
            credentials=credentials,
            project=credentials.project_id,
        )
    else:
        return bigquery.Client()


def upload(key_path, table_id, data):
    client = Client(key_path)
    project_id, dataset_id, table_id = table_id.split(".")

    dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset.location = "US"

    # Raises google.api_core.exceptions.Conflict if the Dataset exists.
    try:
        dataset = client.create_dataset(dataset, timeout=30)
    except Conflict:
        pass

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
    )

    resource = f"{project_id}.{dataset_id}.{table_id}"
    job = client.load_table_from_file(data, resource, job_config=job_config)
    job.result()


def delete(ctx, table_id):
    client = ctx.obj["BigQueryClient"]
    client.delete_table(table_id, not_found_ok=True)
    print(f"Deleted table '{table_id}'")
