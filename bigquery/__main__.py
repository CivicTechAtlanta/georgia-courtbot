import click
from google.api_core.exceptions import Conflict
from google.cloud import bigquery
from google.oauth2 import service_account


def Client(key_path):
    credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    return bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )


@click.group()
@click.pass_context
@click.option(
    "--key-path",
    type=click.Path(exists=True),
    required=True,
    help="Google API service account credential file",
)
def cli(ctx, key_path):
    ctx.ensure_object(dict)
    ctx.obj["BigQueryClient"] = Client(key_path)


@cli.command()
@click.pass_context
@click.option(
    "--dataset_id",
    type=str,
    required=True,
    help="BigQuery Dataset Id",
)
@click.option(
    "--table_id",
    type=str,
    required=True,
    help="BigQuery Table Id",
)
@click.option(
    "--data", type=click.File("rb"), required=True, help="Data to import in CSV format"
)
def upload(ctx, dataset_id, table_id, data):
    client = ctx.obj["BigQueryClient"]
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
    )

    resource = f"{client.project}.{dataset_id}.{table_id}"
    job = client.load_table_from_file(data, resource, job_config=job_config)
    job.result()
    table = client.get_table(resource)

    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), resource
        )
    )


@cli.command()
@click.pass_context
@click.option(
    "--dataset_id",
    type=str,
    required=True,
    help="BigQuery Dataset Id" "--table_id",
)
@click.option(
    "--table_id",
    type=str,
    required=True,
    help="BigQuery Table Id",
)
def delete(ctx, dataset_id, table_id):
    client = ctx.obj["BigQueryClient"]
    fqp = f"{client.project}.{dataset_id}.{table_id}"
    client.delete_table(fqp, not_found_ok=True)  # Make an API request.
    print(f"Deleted table '{fqp}'")


@cli.command()
@click.pass_context
@click.option(
    "--dataset_id",
    type=str,
    required=True,
    help="BigQuery Dataset Id" "--table_id",
)
@click.option(
    "--table_id",
    type=str,
    required=True,
    help="BigQuery Table Id",
)
def create(ctx, dataset_id, table_id):
    client = ctx.obj["BigQueryClient"]
    dataset = bigquery.Dataset(f"{client.project}.{dataset_id}")
    dataset.location = "US"

    # Raises google.api_core.exceptions.Conflict if the Dataset exists.
    try:
        dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
    except Conflict:
        print("Dataset already exists.")
        pass
    except Exception as e:
        print(e)
        return

    schema = [
        bigquery.SchemaField("CaseId", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("CaseNumber", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("JudicialOfficer", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("HearingDate", "DATE", mode="NULLABLE"),
        bigquery.SchemaField("HearingTime", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("CourtRoom", "STRING", mode="NULLABLE"),
    ]

    try:
        table = bigquery.Table(
            f"{client.project}.{dataset_id}.{table_id}", schema=schema
        )
        table = client.create_table(table)  # Make an API request.
        print(
            "Created table {}.{}.{}".format(
                table.project, table.dataset_id, table.table_id
            )
        )
    except Conflict:
        print("Table already exists.")
    except Exception as e:
        print(e)
        return


cli()
