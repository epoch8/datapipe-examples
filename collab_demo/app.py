from sqlalchemy import Column, String, Integer

from datapipe.compute import Catalog
from datapipe.compute import DatapipeApp
from datapipe.compute import Pipeline
from datapipe.compute import Table
from datapipe.executor import ExecutorConfig
from datapipe.datatable import DataStore
from datapipe.step.batch_transform import BatchTransform
from datapipe.store.database import DBConn, TableStoreDB

from lib.file_list import ScanFileList
from transformations import parse_cars, agg__price_by_manufacture_country


FILEPATH__RAW__CARS = "data/raw/cars/{file_name}.json"
FILEPATH__PRICE_BY_MANUFACTURE_COUNTRY = "data/processed/price_by_manufacture_country/{file_name}.json"


try:
    import pysqlite3
    sqla_engine = "sqlite+pysqlite3"
except ImportError:
    sqla_engine = "sqlite"


dbconn = DBConn(f"{sqla_engine}:///store.sqlite")
ds = DataStore(dbconn)


catalog = Catalog(
    {
        "cars_parsed": Table(
            store=TableStoreDB(
                dbconn=dbconn,
                name="cars_parsed",
                data_sql_schema=[
                    Column("file_name", String, primary_key=True),
                    Column("filepath", String),
                    Column("model_id", Integer, primary_key=True),
                    Column("manufacture_country", String, primary_key=True),
                    Column("color", String, primary_key=True),
                ],
            )
        ),
        "price_by_manufacture_country": Table(
            store=TableStoreDB(
                dbconn=dbconn,
                name="price_by_manufacture_country",
                data_sql_schema=[
                    Column("manufacture_country", String, primary_key=True),
                    Column("filepath", String),
                ],
            )
        ),
    }
)


pipeline = Pipeline(
    [
        ScanFileList(
            FILEPATH__RAW__CARS,
            output="cars_scanned",
            labels=[
                ("entity", "cars"),
                ("layer", "scan"),
                ("environment", "prod"),
            ],
        ),
        BatchTransform(
            parse_cars,
            inputs=["cars_scanned"],
            outputs=["cars_parsed"],
            kwargs={},
            chunk_size=1,
            executor_config=ExecutorConfig(parallelism=1),
            transform_keys=[
                "file_name",
            ],
            labels=[
                ("entity", "cars"),
                ("layer", "parse"),
                ("environment", "prod"),
            ],
        ),
        BatchTransform(
            agg__price_by_manufacture_country,
            inputs=["cars_parsed"],
            outputs=["price_by_manufacture_country"],
            kwargs={
                "filepath__price_by_manufacture_country": FILEPATH__PRICE_BY_MANUFACTURE_COUNTRY,
            },
            chunk_size=1,
            executor_config=ExecutorConfig(parallelism=1),
            transform_keys=[
                "manufacture_country",
            ],
            labels=[
                ("entity", "cars"),
                ("layer", "agg"),
                ("environment", "prod"),
            ],
        ),
    ]
)


app = DatapipeApp(ds, catalog, pipeline)
