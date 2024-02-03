from openai import OpenAI, OpenAIError
import pandas as pd
from sqlalchemy import Column, Integer, String

# Import Datapipe modules for data processing, pipeline management, and database operations
from datapipe.compute import Catalog, DatapipeApp, Pipeline, Table
from datapipe.datatable import DataStore
from datapipe.step.batch_transform import BatchTransform
from datapipe.step.update_external_table import UpdateExternalTable
from datapipe.store.database import DBConn
from datapipe.store.pandas import TableStoreExcel

# OpenAI API key (replace with actual key)
GPT_KEY = "WRITE YOUR OPENAI KEY HERE"

# Handle SQLite engine based on OS; this supports the database for storing prompts and results
try:
    # On linux, use pysqlite3
    import pysqlite3

    sqla_engine = "sqlite+pysqlite3"
except ImportError:
    # On mac and windows, try to fallback to sqlite
    sqla_engine = "sqlite"

# Establish database connections for the application
# Database to store Datapipe's internal state
dbconn = DBConn(f"{sqla_engine}:///db.sqlite")
ds = DataStore(dbconn)
# Database to store examples, prompts and processing results
dbconn_data = DBConn(f"{sqla_engine}:///data.sqlite")


# Define a function to process prompts using OpenAI's GPT model
# This function is called by Datapipe to process new or modified prompts and examples
def process_prompt(
    prompt_df: pd.DataFrame,
    input_df: pd.DataFrame,
) -> pd.DataFrame:

    # Creating an OpenAI client instance
    openai_client = OpenAI(api_key=GPT_KEY)

    results = []
    # Iterating through input and prompt dataframes
    for _, inp in input_df.iterrows():
        for _, prompt in prompt_df.iterrows():
            # Generating chat completions using OpenAI GPT
            chat_completion = openai_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt['prompt_text'],
                    },
                    {
                        "role": "user",
                        "content": inp['input_text'],
                    },
                ],
                model="gpt-3.5-turbo",
            )

            # Extracting the answer from the response
            answer = chat_completion.choices[0].message.content

            results.append(
                (
                    prompt['prompt_id'],
                    inp['input_id'],
                    prompt['prompt_text'],
                    inp['input_text'],
                    answer,
                )
            )

    # Returning the results as a DataFrame
    return pd.DataFrame(
        results,
        columns=[
            "prompt_id",
            "input_id",
            "prompt_text",
            "input_text",
            "answer_text",
        ],
    )


# Setting up a catalog to manage tables for prompts, inputs, and outputs
# This structure facilitates the tracking of what needs to be processed
catalog = Catalog(
    {
        "prompt": Table(
            store=TableStoreExcel(
                filename='prompt.xlsx',
                primary_schema=[
                    Column("prompt_id", Integer, primary_key=True),
                    Column("prompt_text", String),
                ],
            )
        ),
        "input": Table(
            store=TableStoreExcel(
                filename='input.xlsx',
                primary_schema=[
                    Column("input_id", Integer, primary_key=True),
                    Column("input_text", String),
                ],
            )
        ),
        "output": Table(
            store=TableStoreExcel(
                filename='output.xlsx',
                primary_schema=[
                    Column("prompt_id", Integer, primary_key=True),
                    Column("input_id", Integer, primary_key=True),
                    Column("prompt_text", String),
                    Column("input_text", String),
                    Column("answer_text", String),
                ],
            )
        ),
    }
)

# Defining the pipeline for data processing
# This pipeline dictates how data flows through the system and is processed
pipeline = Pipeline(
    [
        # Update tables with new or modified prompts and inputs
        UpdateExternalTable(
            output="prompt",
        ),
        UpdateExternalTable(
            output="input",
        ),
        # Apply transformation to process only new or modified data
        BatchTransform(
            process_prompt,
            inputs=["prompt", "input"],
            outputs=["output"],
            transform_keys=[
                "prompt_id",
                "input_id",
            ],
            chunk_size=100,
        ),
    ]
)


app = DatapipeApp(ds, catalog, pipeline)
