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
                "filepath": row["filepath"],
                "model_id": json_record["model_id"],
                "manufacture_country": json_record["manufacture_country"],
                "color": json_record["color"],
            },
            index=[0]
        )

        list_output_dfs.append(df__record_parsed)

    df__output__cars_parsed = pd.concat(list_output_dfs)

    return df__output__cars_parsed


def agg__price_by_manufacture_country(
        df__input__cars_parsed: pd.DataFrame,
        filepath__price_by_manufacture_country: str
) -> pd.DataFrame:
    df__data__price_by_manufacture_country = pd.concat(
        [
            pd.read_json(row["filepath"], typ="series").to_frame().T[["manufacture_country", "price"]]
            for _, row in df__input__cars_parsed.iterrows()
        ]
    )

    df__data__price_by_manufacture_country = df__data__price_by_manufacture_country.groupby("manufacture_country").sum()
    df__data__price_by_manufacture_country.to_json(
        filepath__price_by_manufacture_country.format(file_name=df__data__price_by_manufacture_country.index[0]),
        orient="records",
    )

    df__output__price_by_manufacture_country = df__input__cars_parsed[["manufacture_country"]]
    df__output__price_by_manufacture_country = df__output__price_by_manufacture_country.drop_duplicates(ignore_index=True, keep="first")

    return df__output__price_by_manufacture_country
