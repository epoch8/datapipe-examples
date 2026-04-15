import os
import re
import time
from pathlib import Path
from typing import List, Optional

import fsspec
import pandas as pd
from datapipe.compute import Catalog, ComputeStep, PipelineStep, Table
from datapipe.step.datatable_transform import DatatableTransformStep
from datapipe.datatable import DataStore, DataTable
from datapipe.run_config import RunConfig
from datapipe.store.database import TableStoreDB
from datapipe.store.filedir import TableStoreFiledir, JSONFile
from datapipe.store.pandas import TableStoreJsonLine
from datapipe.store.filedir import (
    _pattern_to_attrnames,
    _pattern_to_glob,
    _pattern_to_match,
    _pattern_to_patterns_or,
)
from datapipe.types import Labels
from sqlalchemy import Column, Integer, String

FILES_SCHEMA = [
    Column("filepath", String()),
    Column("size_bytes", Integer()),
]


class ScanFileList(PipelineStep):
    def __init__(
        self,
        filename_pattern: str,
        output: str,
        labels: Optional[Labels] = None,
    ):
        self.output = output
        self.filename_pattern = filename_pattern
        self.labels = labels

    def build_compute(self, ds: DataStore, catalog: Catalog) -> List[ComputeStep]:
        attrnames = _pattern_to_attrnames(self.filename_pattern)

        catalog.add_datatable(
            name=self.output,
            dt=Table(
                store=TableStoreJsonLine(
                    filename=self.filename_pattern.format(data=self.output),
                    primary_schema=[
                        Column(attrname, String(), primary_key=True)
                        for attrname in attrnames
                    ]
                    + FILES_SCHEMA,
                )
            ),
        )

        output_table = catalog.get_datatable(ds, self.output)

        return [
            DatatableTransformStep(
                name=f"scan_file_list__{self.output}",
                input_dts=[],
                output_dts=[output_table],
                func=scan_file_list,
                kwargs={"filename_pattern": self.filename_pattern},
                labels=self.labels,
            )
        ]


def scan_file_list(
    ds: DataStore,
    input_dts: List[DataTable],
    output_dts: List[DataTable],
    run_config: Optional[RunConfig],
    kwargs: dict,
) -> None:
    [output_dt] = output_dts
    now = time.time()

    filename_pattern = kwargs["filename_pattern"]

    protocol, path = fsspec.core.split_protocol(filename_pattern)

    if protocol is None or protocol == "file":
        filename_pattern = str(Path(path).resolve())
        filename_pattern_for_match = filename_pattern
        protocol_str = "" if protocol is None else "file://"
    else:
        filename_pattern = str(filename_pattern)
        filename_pattern_for_match = path
        protocol_str = f"{protocol}://"

    filename_patterns = _pattern_to_patterns_or(filename_pattern)
    attrnames = _pattern_to_attrnames(filename_pattern)
    filename_glob = [_pattern_to_glob(pat) for pat in filename_patterns]
    filename_match = _pattern_to_match(filename_pattern_for_match)

    files = fsspec.open_files(filename_glob)

    res = []

    for f in files:
        item = {
            "filepath": f"{protocol_str}{os.path.relpath(f.path)}",
            "size_bytes": files.fs.size(f.path),
        }

        m = re.match(filename_match, f.path)

        assert m is not None
        for attrname in attrnames:
            item[attrname] = m.group(attrname)

        res.append(item)

    output_dt.store_chunk(pd.DataFrame(res), now=now, run_config=run_config)
    output_dt.delete_stale_by_process_ts(now, now=now, run_config=run_config)
