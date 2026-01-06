import pandas as pd
import sqlite3

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from datapipe.compute import Catalog
from datapipe.compute import DatapipeApp
from datapipe.compute import Pipeline
from datapipe.compute import Table
from datapipe.datatable import DataStore
from datapipe.step.batch_transform import BatchTransform
from datapipe.step.update_external_table import UpdateExternalTable
from datapipe.store.database import DBConn, TableStoreDB

from RUN_ME import PATH__DATA


try:
    import pysqlite3
    sqla_engine = "sqlite+pysqlite3"
except ImportError:
    sqla_engine = "sqlite"


dbconn = DBConn(f"{sqla_engine}:///datapipe.sqlite")
ds = DataStore(dbconn)
dbconn_data = DBConn(f"{sqla_engine}:///data.sqlite")


def replace_word(
    df__input: pd.DataFrame,
) -> pd.DataFrame:
    
    results = []
    for _, row__input in df__input.iterrows():
         
        # connection__data = sqlite3.connect(PATH__DATA)
        # df = pd.read_sql_query(
        #     "SELECT * FROM input",
        #     connection__data,
        # )
        # df["output_id"] = df["input_id"]
        # df["output_text"] = df["input_text"].apply(lambda x: x.replace("World", "Kitty"))
        # df.to_sql(
        #     "output",
        #     connection__data,
        #     if_exists="append",
        #     index=False,
        # )

        tranformation = row__input['input_text'].replace(
            "World",
            "Kitty"
        )

        results.append(
            (
                row__input["input_id"],
                row__input["input_id"],
                row__input["input_text"],
                tranformation
            )
        )

    return pd.DataFrame(
        results,
        columns=[
            "input_id",
            "output_id",
            "input_text",
            "output_text"
        ],
    )     


catalog = Catalog(
    {
        "input": Table(
            store=TableStoreDB(
                dbconn=dbconn_data,
                name="input",
                data_sql_schema=[
                    Column("input_id", Integer, primary_key=True),
                    Column("input_text", String),
                ],
                create_table=True,
            )
        ),
        "output": Table(
            store=TableStoreDB(
                dbconn=dbconn_data,
                name='output',
                data_sql_schema=[
                    # Column("input_id", Integer, primary_key=True),
                    Column("input_id", Integer),
                    Column("output_id", Integer, primary_key=True),
                    Column("input_text", String),
                    Column("output_text", String),
                ],
                create_table=True,
            )
        ),
    }
)


pipeline = Pipeline(
    [
        UpdateExternalTable(
            output="input",
        ),
        BatchTransform(
            replace_word,
            inputs=["input"],
            outputs=["output"],
            transform_keys=[
                "input_id",
            ],
            chunk_size=100,
        ),
    ]
)


app = DatapipeApp(ds, catalog, pipeline)
