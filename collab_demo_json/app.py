from sqlalchemy import Column, String, Integer

from datapipe.compute import Catalog
from datapipe.compute import DatapipeApp
from datapipe.compute import Pipeline
from datapipe.compute import Table
from datapipe.executor import ExecutorConfig
from datapipe.datatable import DataStore
from datapipe.step.batch_transform import BatchTransform
from datapipe.store.database import DBConn
from datapipe.store.pandas import TableStoreJsonLine

from lib.file_list import ScanFileList
from transformations import parse_cars
from transformations import agg__price_by_manufacture_country
from transformations import agg__price_by_color
from transformations import agg__price_by_manufacture_country_and_color


FILEPATH__RAW__CARS = "data/raw/cars/{file_name}.json"
FILEPATH__PROCESSED__CARS = "data/processed/cars/{data}.jsonl"


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
            store=TableStoreJsonLine(
                filename=FILEPATH__PROCESSED__CARS.format(data="cars_parsed"),
                primary_schema=[
                    Column("file_name", String, primary_key=True),
                    Column("model_id", Integer, primary_key=True),
                    Column("manufacture_country", String, primary_key=True),
                    Column("color", String, primary_key=True),
                ],
            )
        ),
        "price_by_manufacture_country": Table(
            store=TableStoreJsonLine(
                filename=FILEPATH__PROCESSED__CARS.format(data="price_by_manufacture_country"),
                primary_schema=[
                    Column("manufacture_country", String, primary_key=True),
                ],
            )
        ),
        "price_by_color": Table(
            store=TableStoreJsonLine(
                filename=FILEPATH__PROCESSED__CARS.format(data="price_by_color"),
                primary_schema=[
                    Column("color", String, primary_key=True),
                ],
            )
        ),
        "price_by_manufacture_country_and_color": Table(
            store=TableStoreJsonLine(
                filename=FILEPATH__PROCESSED__CARS.format(data="price_by_manufacture_country_and_color"),
                primary_schema=[
                    Column("manufacture_country", String, primary_key=True),
                    Column("color", String, primary_key=True),
                ],
            )
        ),
    }
)


pipeline = Pipeline(
    [
        ScanFileList(
            filename_pattern=FILEPATH__RAW__CARS,
            filename_output=FILEPATH__PROCESSED__CARS,
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
            kwargs={},
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
        BatchTransform(
            agg__price_by_color,
            inputs=["cars_parsed"],
            outputs=["price_by_color"],
            kwargs={},
            chunk_size=1,
            executor_config=ExecutorConfig(parallelism=1),
            transform_keys=[
                "color",
            ],
            labels=[
                ("entity", "cars"),
                ("layer", "agg"),
                ("environment", "prod"),
            ],
        ),
        BatchTransform(
            agg__price_by_manufacture_country_and_color,
            inputs=["cars_parsed"],
            outputs=["price_by_manufacture_country_and_color"],
            kwargs={},
            chunk_size=1,
            executor_config=ExecutorConfig(parallelism=1),
            transform_keys=[
                "manufacture_country",
                "color",
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
