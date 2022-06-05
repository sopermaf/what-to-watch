"""
Convert movies
"""
import csv

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

from movies.models import WatchItem


class Command(BaseCommand):
    help = "Import imdb data to DB"

    def add_arguments(self, parser):
        parser.add_argument("files", nargs="+", type=str)

    def handle(self, *args, **options):
        # TODO: download new files
        self.stdout.write("Downloading new data")

        # TODO: import data into DB
        for file in options["files"]:
            with open(settings.BASE_DIR / file):
                pass

        self.stdout.write("Transforming data")
        # # NOTE: "title.basics.tsv", "title.ratings.tsv" required
        # imdb_df = title_csv_to_dfs(*options["files"])
        # imdb_df = filter_imdb_df(imdb_df)
        # imdb_df.to_csv("example.csv")

        self.stdout.write("Importing data to db")
        self.import_into_csv(settings.BASE_DIR / "example.csv")

        self.stdout.write(self.style.SUCCESS("DONE!"))

    def import_into_csv(self, csv_file: str) -> None:
        with open(csv_file) as fp:
            for line in csv.DictReader(fp):
                try:
                    WatchItem.create_watch_item(line)
                except Exception:
                    self.stdout.write(f"Error for {line['primaryTitle']=}")
                else:
                    self.stdout.write(f"Success! - {line['primaryTitle']=}")


def load_imdb_csv(filename) -> pd.DataFrame:
    return pd.read_csv(filename, sep="\t", index_col="tconst")


def title_csv_to_dfs(*filenames):
    """
    Assumes tconst for id and tsv
    """
    first, *rest = filenames
    first_df = load_imdb_csv(first)
    return first_df.join(list(map(load_imdb_csv, rest)))


def filter_imdb_df(imdb_df):
    for col in ("averageRating", "numVotes", "startYear"):
        imdb_df[col] = pd.to_numeric(imdb_df[col], errors="coerce")

    # TODO: change, temporary filters to reduce data size
    imdb_df = imdb_df.loc[
        (imdb_df["isAdult"] == 0)
        & (imdb_df["titleType"] == "movie")
        & (imdb_df["numVotes"] >= 5000)
        & (imdb_df["startYear"] >= 1980)
    ]
    return imdb_df
