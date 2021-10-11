import datetime
import json
from collections import namedtuple
from typing import List, Tuple

import pandas as pd
import pyspark.sql.functions as F
from grimoire.decorators import notify_execution
from grimoire.file import write_file
from grimoire.search_run.entries.main import Configuration

from search_run.data_paths import DataPaths
from search_run.observability.logger import configure_logger
from search_run.ranking.ciclical_placement import CiclicalPlacement

logger = configure_logger()


class Ranking:
    """
    Write to the file all the commands and generates shortcuts
    """

    ModelInfo = namedtuple("ModelInfo", "features label")
    model_info = ModelInfo(["position", "key_lenght"], "input_lenght")

    def __init__(self):
        self.configuration = Configuration
        self.cached_file = Configuration.cached_filename

    @notify_execution()
    def recompute_rank(self):
        """
        Recomputes the rank and saves the results on the file to be read
        """

        entries: dict = self.load_entries()
        commands_performed = self.load_commands_performed_df()
        result = CiclicalPlacement().cyclical_placment(entries, commands_performed)

        return self._export_to_file(result)

    def compute_head(self):
        from pyspark.sql.session import SparkSession

        spark = SparkSession.builder.getOrCreate()
        entries_df: dict = self.load_entries_df(spark)
        performed_df = self.load_commands_performed_dataframe(spark)
        joined = (
            entries_df.join(
                performed_df, performed_df.key == entries_df.key, how="left"
            )
            .groupBy(entries_df.key)
            .agg(
                F.first(entries_df.created_at).alias("created_at"),
                F.last(performed_df.generated_date).alias("latest_executed"),
            )
        )
        joined = joined.withColumn(
            "latest_event",
            F.when(
                joined.latest_executed.isNotNull(), joined.latest_executed
            ).otherwise(joined.created_at),
        )
        joined = (
            joined.withColumn("unix", F.unix_timestamp("latest_event"))
            .orderBy("unix", desc=True)
            .show()
        )
        breakpoint()

        joined = joined.select("key").limit(30)
        result = joined.collect()
        final_result = list(map(lambda x: x.key, result))

        return final_result

    def load_commands_performed_df(self):
        """
        Returns a pandas datafarme with the commands performed
        """
        with open(DataPaths.commands_performed) as f:
            data = []
            for line in f.readlines():
                try:
                    data_entry = json.loads(line)
                    dt = datetime.datetime.strptime(
                        data_entry["generated_date"], "%Y-%m-%d %H:%M:%S"
                    )
                    data_entry["generated_date"] = dt
                    data.append(data_entry)
                except BaseException:
                    logger.info(f"Line broken: {line}")
        df = pd.DataFrame(data)

        # revert the list (latest on top)
        df = df.iloc[::-1]

        return df

    def load_commands_performed_dataframe(self, spark):
        dataset = Ranking().load_commands_performed_df()
        schema = "`key` STRING,  `generated_date` TIMESTAMP, `uuid` STRING, `given_input` STRING"
        original_df = spark.createDataFrame(dataset, schema=schema)
        performed_df = original_df.withColumn("input_lenght", F.length("given_input"))
        performed_df = performed_df.filter('given_input != "NaN"')
        performed_df = performed_df.drop("uuid")

        return performed_df

    def load_entries_df(self, spark):
        """
        loads a spark dataframe with the configuration entries
        """
        real_entries = self.load_entries()
        entries = []

        default_created_at = datetime.datetime(2020, 1, 1, 00, 00)

        for position, entry in enumerate(real_entries.items()):
            created_at = (
                entry[1].get("created_at", default_created_at)
                if type(entry[1]) is dict
                else default_created_at
            )
            transformed_entry = {
                "key": entry[0],
                "content": f"{entry[1]}",
                "created_at": created_at,
                "position": position + 1,
            }
            entries.append(transformed_entry)

        rdd = spark.sparkContext.parallelize(entries)
        schema = "`key` STRING,  `content` STRING, `created_at` TIMESTAMP, `position` INTEGER"
        entries_df = spark.read.json(rdd, schema=schema)
        entries_df = entries_df.drop("_corrupt_record")
        entries_df = entries_df.withColumn("key_lenght", F.length("key"))

        return entries_df

    def dump_entries(self):
        """
        Dump entries to be consumed into the feature store
        """
        import datetime

        from pyspark.sql import functions as F
        from pyspark.sql.session import SparkSession

        spark = SparkSession.builder.getOrCreate()
        df = self.load_entries_df(spark)

        df = df.withColumn(
            "event_timestamp",
            F.lit(datetime.datetime.now().timestamp()).cast("timestamp"),
        )
        df = df.withColumnRenamed("key", "entry_key")

        df.repartition(1).write.mode("overwrite").parquet(DataPaths.entries_dump)

        import os
        import pathlib

        current_file_name = str(
            list(pathlib.Path(DataPaths.entries_dump).glob("*.parquet"))[0]
        )
        os.rename(current_file_name, DataPaths.entries_dump + "/000.parquet")

    def load_entries(self):
        """ Loads the current state of the art of search run entries"""
        return self.configuration().commands

    def _export_to_file(self, data: List[Tuple[str, dict]]):
        fzf_lines = ""
        position = 1
        for name, content in data:
            try:
                content["key_name"] = name
                content["rank_position"] = position
                content = json.dumps(content, default=tuple, ensure_ascii=True)
            except BaseException:
                content = content
                content = str(content)

            position = position + 1
            fzf_lines += f"{name.lower()}: " + content + "\n"

        fzf_lines = fzf_lines.replace("\\", "\\\\")
        write_file(self.configuration.cached_filename, fzf_lines)
