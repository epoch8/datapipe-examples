import json
import pandas as pd


"""
===== NAMING CONVENTION =====

df__***             - Pandas dataframe;
df_pl__***          - Polars dataframe;
filepath__***       - string with filepath;
meta__***           - meta-information about output data;

***__input__***     - input object;
***__prev__***      - previous chain object;
***__output__***    - output object.
***__data__***      - data object.
"""


def parse_cars(df__input__cars_scanned: pd.DataFrame) -> pd.DataFrame:
    list_output_dfs = []

    for _, row in df__input__cars_scanned.iterrows():
        with open(row["filepath"], "r") as file:
            json_record = json.load(file)

        df__record_parsed = pd.DataFrame(
            {
                "file_name": row["file_name"],
                "model_id": json_record["model_id"],
                "manufacture_country": json_record["manufacture_country"],
                "color": json_record["color"],
                "price": json_record["price"],
                "year": json_record["year"],
                "new": json_record["new"],
            },
            index=[0]
        )

        list_output_dfs.append(df__record_parsed)

    df__output__cars_parsed = pd.concat(list_output_dfs)

    return df__output__cars_parsed


def agg__price_by_manufacture_country(
        df__input__cars_parsed: pd.DataFrame,
) -> pd.DataFrame:
    df__output__price_by_manufacture_country = df__input__cars_parsed[["manufacture_country", "price"]]
    df__output__price_by_manufacture_country = (
        df__output__price_by_manufacture_country
        .groupby("manufacture_country", as_index=False)
        .sum()
    )

    return df__output__price_by_manufacture_country


def agg__price_by_color(
        df__input__cars_parsed: pd.DataFrame,
) -> pd.DataFrame:
    df__output__price_by_color = df__input__cars_parsed[["color", "price"]]
    df__output__price_by_color = (
        df__output__price_by_color
        .groupby("color", as_index=False)
        .sum()
    )

    return df__output__price_by_color


def agg__price_by_manufacture_country_and_color(
        df__input__cars_parsed: pd.DataFrame,
) -> pd.DataFrame:
    df__output__price_by_manufacture_country_and_color = df__input__cars_parsed[["manufacture_country", "color", "price"]]
    df__output__price_by_manufacture_country_and_color = (
        df__output__price_by_manufacture_country_and_color
        .groupby(["manufacture_country", "color"], as_index=False)
        .sum()
    )

    return df__output__price_by_manufacture_country_and_color
