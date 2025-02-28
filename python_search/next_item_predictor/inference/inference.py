from __future__ import annotations

import os
from typing import Any, List, Optional

from python_search.configuration.configuration import PythonSearchConfiguration
from python_search.configuration.loader import ConfigurationLoader
from python_search.events.latest_used_entries import RecentKeys
from python_search.infrastructure.performance import timeit
from python_search.logger import setup_inference_logger
from python_search.next_item_predictor.inference.input import ModelInput


class Inference:
    """
    Performs the search inference on all existing keys in the moment
    """

    def __init__(
        self,
        configuration: Optional[PythonSearchConfiguration] = None,
        run_id: Optional[str] = None,
        model: Optional[Any] = None,
        logger=None,
    ):
        self.debug = os.getenv("DEBUG", False)

        configuration = (
            configuration if configuration else ConfigurationLoader().load_config()
        )
        self.all_keys = configuration.commands.keys()
        self._model = configuration.get_next_item_predictor_model()

        self.run_id = run_id if run_id else self._model.get_run_id()

        self._logger = logger if logger else setup_inference_logger()
        if model:
            self._logger.info("Using custom passed model")
        else:
            self._logger.debug("Next item predictor using run id: " + self.run_id)

        try:
            self._mlflow_model = (
                model if model else self._model.load_mlflow_model(run_id=self.run_id)
            )
        except Exception as e:
            print("Failed to load mlflow model")
            self._mlflow_model = None
            raise e

        self._recent_keys = RecentKeys().get_latest_used_keys(history_size=2)

    @timeit
    def get_ranking(self, predefined_input: Optional[ModelInput] = None) -> List[str]:
        """
        Gets the search from the next item _model
        """
        self._logger.debug(
            "Number of existing keys for inference: " + str(len(self.all_keys))
        )
        inference_input = (
            predefined_input
            if predefined_input
            else ModelInput.with_given_keys(self._recent_keys[0], self._recent_keys[1])
        )
        self._logger.debug("Inference input: " + str(inference_input.__dict__))

        X = self._model.transform_single(
            {"inference_input": inference_input, "all_keys": self.all_keys}
        )
        Y = self._predict(X)
        result = list(zip(self.all_keys, Y))
        result.sort(key=lambda x: x[1], reverse=True)

        only_keys = [entry[0] for entry in result]
        self._logger.debug(
            "Ranking inference succeeded, top results {}".format(only_keys[:3])
        )

        return only_keys

    @timeit
    def _predict(self, X):
        return self._mlflow_model.predict(X)
