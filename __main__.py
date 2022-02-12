import click
import data.dekalb_scraper
import bigquery.commands


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--output",
    type=click.Choice(["csv", "json"]),
    help="Format to use when reporting scraped data.",
)
@click.option(
    "--days",
    type=int,
    default=90,
    help="How many days of data to scrape, measured from today. Default is 90 days.",
)
def scrape(output, days):
    data.dekalb_scraper.run(output, days)


@cli.command()
@click.option(
    "--key-path",
    type=click.Path(exists=True),
    required=False,
    help="Google API service account credential file",
)
@click.option(
    "--table-id",
    type=str,
    required=True,
    help="BigQuery Table Id as a fully qualifed name: 'project.dataset.table'",
)
@click.option(
    "--data", type=click.File("rb"), required=True, help="Data to import in CSV format"
)
def upload(key_path, table_id, data):
    bigquery.commands.upload(key_path, table_id, data)


cli()
