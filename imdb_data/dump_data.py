import pandas as pd


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


if __name__ == "__main__":
    imdb_df = title_csv_to_dfs("title.basics.tsv", "title.ratings.tsv")
    imdb_df = filter_imdb_df(imdb_df)
    imdb_df.to_csv("example.csv")
