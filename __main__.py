import click
import data.dekalb_scraper


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


cli()
