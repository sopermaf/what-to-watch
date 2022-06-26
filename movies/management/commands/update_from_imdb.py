"""
Downloads data from imdb and loads files
"""
import csv
from pathlib import Path
from tempfile import TemporaryFile

import pandas as pd
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from marshmallow import Schema, fields, pre_load
from tqdm import tqdm

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
        data.update({k: None for k, v in data.items() if not v or v == r"\N"})

        genres = (data["genres"] or "").split(",")
        data["genres"] = genres if any(genres) else []

        return data


class Command(BaseCommand):
    help = "Import imdb data to DB"
    required_files = ("title.ratings.tsv.gz", "title.basics.tsv.gz")

    def add_arguments(self, parser):
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

    @staticmethod
    def download_imdb_file(filename, chunk_size=128) -> Path:
        """
        Downloads the imdb file to root directory
        """
        path = settings.BASE_DIR / filename
        with open(path, "wb+") as fp:
            resp = requests.get(f"https://datasets.imdbws.com/{filename}", stream=True)
            resp.raise_for_status()

            content_chunks = resp.iter_content(chunk_size=chunk_size)
            num_chunks = int(resp.headers["Content-Length"]) / chunk_size

            for chunk in tqdm(content_chunks, total=num_chunks):
                fp.write(chunk)

        return path

    def handle(self, *args, **options):
        files = [settings.BASE_DIR / f for f in self.required_files]
        # download the files from imdb data source
        if options["download"]:
            self.stdout.write("Downloading new data")
            files = list(map(self.download_imdb_file, self.required_files))

        self.stdout.write(f"Transforming data: {files}")
        imdb_df = title_csv_to_dfs(*files)
        imdb_df = filter_imdb_df(imdb_df)

        # temporary CSV file between dataframe to database
        with TemporaryFile(mode="w+") as fp:
            imdb_df.to_csv(fp)

            self.stdout.write("Importing data to db")
            fp.seek(0)
            self.import_into_csv(fp, imdb_df.shape[0])

        self.stdout.write(self.style.SUCCESS("DONE!"))

    @staticmethod
    def import_into_csv(csv_file, total: int) -> None:
        for line in tqdm(csv.DictReader(csv_file), total=total):
            WatchItem.create_watch_item(WatchItemSchema().load(line))


def load_imdb_csv(filename) -> pd.DataFrame:
    return pd.read_csv(filename, sep="\t", index_col="tconst", compression="gzip")


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
        & (imdb_df["numVotes"] >= 50000)
        & (imdb_df["startYear"] >= 1980)
    ]
    return imdb_df
