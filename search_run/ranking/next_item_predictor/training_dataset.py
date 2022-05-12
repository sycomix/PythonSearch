import logging
import os.path
import sys

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.window import Window

from search_run.datasets.searchesperformed import SearchesPerformed


class TrainingDataset:
    """
    Builds the dataset ready for training
    """

    columns = "key", "previous_key", "week", "label"

    def __init__(self):
        self._spark = SparkSession.builder.getOrCreate()
        logging.basicConfig(
            level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)]
        ),

    def build(self, use_cache=False, write_cache=True):
        """When cache is enabled, writes a parquet in a temporary file"""
        if use_cache:
            if os.path.exists("/tmp/dataset"):
                print("Reading cache dataset")
                return self._spark.read.parquet("/tmp/dataset")
            else:
                print("Cache does not exist, creating dataset")

        search_performed_df = SearchesPerformed(self._spark).load()

        # filter out too common keys
        excluded_keys = ["startsearchrunsearch", "search run search focus or open", ""]
        search_performed_df_filtered = search_performed_df.filter(
            ~F.col("key").isin(excluded_keys)
        )
        logging.info("Loading searches performed")

        # build pair dataset with label
        # add literal column
        search_performed_df_tmpcol = search_performed_df_filtered.withColumn(
            "tmp", F.lit("toremove")
        )
        window = Window.partitionBy("tmp").orderBy("timestamp")

        # add row number to the dataset
        search_performed_df_row_number = search_performed_df_tmpcol.withColumn(
            "row_number", F.row_number().over(window)
        ).sort("timestamp", ascending=False)

        # add previous key to the dataset
        search_performed_df_with_previous = search_performed_df_row_number.withColumn(
            "previous_key", F.lag("key", 1, None).over(window)
        ).sort("timestamp", ascending=False)

        search_performed_df_with_week = search_performed_df_with_previous.withColumn(
            "week", F.weekofyear("timestamp")
        )

        logging.info("Columns added")

        # keep only necessary columns
        pair = search_performed_df_with_week.select(
            "week", "key", "previous_key", "timestamp"
        )

        logging.info("Adding number of times the pair was executed together")
        grouped = (
            pair.groupBy("week", "key", "previous_key")
            .agg(F.count("previous_key").alias("times"))
            .sort("key", "times")
        )

        grouped.cache()
        grouped.count()

        logging.info("Adding label")
        # add the label
        dataset = grouped.withColumn(
            "label",
            F.col("times") / F.sum("times").over(Window.partitionBy("week", "key")),
        ).orderBy("week", "key", "label")
        dataset = dataset.select(*self.columns)

        logging.info("TrainingDataset ready, writing it to disk")
        if write_cache:
            print("Writing cache dataset to disk")
            if os.path.exists("/tmp/dataset"):
                import shutil

                shutil.rmtree("/tmp/dataset")
            dataset.write.parquet("/tmp/dataset")

        logging.info("Printing a sample of the dataset")
        dataset.show(10)
        return dataset


if __name__ == "__main__":
    import fire

    fire.Fire()
