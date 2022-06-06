"""
Downloads data from imdb and loads files
"""
import csv

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from marshmallow import Schema, fields, pre_load

from movies.models import WatchItem


class WatchItemSchema(Schema):
    imdb_id = fields.String(data_key="tconst")
    average_rating = fields.Float(data_key="averageRating")
    num_votes = fields.Number(data_key="numVotes")
    title_type = fields.String(data_key="titleType")
    primary_title = fields.String(data_key="primaryTitle")
    original_title = fields.String(data_key="originalTitle")
    is_adult = fields.Boolean(data_key="isAdult")
    start_year = fields.Number(data_key="startYear", allow_none=True)
    end_year = fields.Number(data_key="endYear", allow_none=True)
    runtime_minutes = fields.Number(data_key="runtimeMinutes", allow_none=True)
    genres = fields.List(fields.String)

    @pre_load
    def clean_values(self, data, **_):
        # remove `\N` for null
        for k, v in data.items():
            if not v or v == r"\N":
                data[k] = None

        # split genre
        try:
            genres = data["genres"].split(",")
        except AttributeError:
            genres = []
        finally:
            data["genres"] = genres if any(genres) else []

        return data


class Command(BaseCommand):
    help = "Import imdb data to DB"
    required_files = ("title.basics.tsv", "title.ratings.tsv")

    def add_arguments(self, parser):
        # parser.add_argument("files", nargs="+", type=str)

        # Named (optional) arguments
        parser.add_argument(
            "--download",
            action="store_true",
            help="Delete poll instead of closing it",
        )

        parser.add_argument(
            "--remove-files",
            action="store_true",
            help="Delete poll instead of closing it",
        )

    def handle(self, *args, **options):
        if options["download"]:
            self.stdout.write("Downloading new data")

        # TODO: add file removal step
        files = [settings.BASE_DIR / file for file in self.required_files]
        # TODO: replace usage with TemporaryNamedFile
        temp_file = str(settings.BASE_DIR / "example.csv")

        self.stdout.write(f"Transforming data: {files}")
        imdb_df = title_csv_to_dfs(*files)
        imdb_df = filter_imdb_df(imdb_df)
        imdb_df.to_csv(temp_file)

        self.stdout.write("Importing data to db")
        self.import_into_csv(temp_file)

        if options["remove-files"]:
            # TODO: remove created temporary files
            pass

        self.stdout.write(self.style.SUCCESS("DONE!"))

    def import_into_csv(self, csv_file: str) -> None:
        with open(csv_file) as fp:
            for line in csv.DictReader(fp):
                WatchItem.create_watch_item(WatchItemSchema().load(line))
                self.stdout.write(f"Success! - {line['primaryTitle']}")


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
