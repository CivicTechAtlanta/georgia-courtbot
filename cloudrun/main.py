from google.cloud import bigquery
from google.api_core.exceptions import NotFound
import os
import requests
from flask import Flask
import sys

from scraper.data.dekalb_scraper import run


app = Flask(__name__)

@app.route("/")
def run_scrape():

    sys.stdout = open('/tmp/temp.csv','w')
    run('csv', 90)
    sys.stdout.close()

    bigquery_client = bigquery.Client()

    table_id = f"{os.environ.get('PROJECT_ID')}.{os.environ.get('DATASET_ID')}.{os.environ.get('TABLE_ID')}"

    try:  
        previous_rows = bigquery_client.get_table(table_id).num_rows
    except NotFound:
        previous_rows = 0

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("CaseId", "INTEGER"),
            bigquery.SchemaField("CaseNumber", "STRING"),
            bigquery.SchemaField("JudicialOfficer", "STRING"),
            bigquery.SchemaField("HearingDate", "STRING"),
            bigquery.SchemaField("HearingTime", "STRING"),
            bigquery.SchemaField("CourtRoom", "STRING"),
        ],
        skip_leading_rows=1,
        # The source format defaults to CSV, so the line below is optional.
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED
    )

    with open('/tmp/temp.csv', "rb") as source_file:
        load_job = bigquery_client.load_table_from_file(source_file, table_id, job_config=job_config)

    load_job.result()  # Waits for the job to complete.

    destination_rows = bigquery_client.get_table(table_id).num_rows

    return f"Loaded {destination_rows-previous_rows} rows."


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))