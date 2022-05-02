"""
Takes data and will transform and load into db
"""
import logging

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

print("Importing Data")
dfs = [
    pd.read_csv(f"imdb_data/title.{file}.tsv", sep="\t").set_index("tconst")
    for file in ("basics", "ratings")
]

print("Dataframes loaded. Combining")
df_combined = dfs[0].join(dfs[1])
print(df_combined.columns)

print("Transforming numeric columns")
df_combined["averageRating"] = pd.to_numeric(
    df_combined["averageRating"], errors="coerce"
)

print("Filtering out uninteresting data")
df_combined = df_combined.loc[
    (df_combined["isAdult"] == 0)
    & (df_combined["titleType"] == "movie")
    & (df_combined["numVotes"] >= 50000)
    & (df_combined["averageRating"] >= 4.0)
]

print("Writing to file")
with open("imdb_data/imdb_combined.csv", "w") as fp:
    df_combined.sample(n=1000).to_csv(fp)

print("Done")
