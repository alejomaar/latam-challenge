import logging
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Example usage
logger = logging.getLogger(__name__)

FEATURES_COLS = [
    "OPERA_Latin American Wings",
    "MES_7",
    "MES_10",
    "OPERA_Grupo LATAM",
    "MES_12",
    "TIPOVUELO_I",
    "MES_4",
    "MES_11",
    "OPERA_Sky Airline",
    "OPERA_Copa Air",
]
THRESHOLD_IN_MINUTES = 15
CORE_COLUMNS = ["OPERA", "TIPOVUELO", "MES"]

folder = Path(__file__).parent
MODEL_PATH = folder / "model" / "model.pkl"
ENCODER_PATH = folder / "model" / "encoder.pkl"


class DelayModel:
    """
    A model for predicting the probability of flight delay at SCL airport.

    Attributes:
        _model: The machine learning model used for delay prediction.
        _encoder: The encoder for preprocessing the input data.
        _target_column (str): The name of the target column (e.g., delay) used in prediction.
    """

    def __init__(self):

        self._model = self.load_pickle(MODEL_PATH)
        self._encoder = self.load_pickle(ENCODER_PATH)
        self._target_column = None

    @staticmethod
    def load_pickle(path: str) -> Optional[object]:
        """Loads a pickle file if it exists, otherwise return None"""
        if os.path.exists(path):
            with open(path, "rb") as file:
                return pickle.load(file)
        logger.warning("%s was no found", path)
        return None

    @staticmethod
    def get_min_diff(data: pd.Series) -> float:
        """
        Calculates the difference in minutes between the scheduled flight
        date (`Fecha-I`) and the actual flight operation date (`Fecha-O`).
        """
        fecha_o = datetime.strptime(data["Fecha-O"], "%Y-%m-%d %H:%M:%S")
        fecha_i = datetime.strptime(data["Fecha-I"], "%Y-%m-%d %H:%M:%S")
        min_diff = ((fecha_o - fecha_i).total_seconds()) / 60
        return min_diff

    def preprocess(
        self, data: pd.DataFrame, target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """

        if target_column:
            # Setup target column
            data["min_diff"] = data.apply(DelayModel.get_min_diff, axis=1)
            data[target_column] = np.where(
                data["min_diff"] > THRESHOLD_IN_MINUTES, 1, 0
            )
            self._target_column = target_column
            # Setup features
            self._encoder = OneHotEncoder(sparse_output=False)
            categorical_df = data[CORE_COLUMNS]
            encoded_features = self._encoder.fit_transform(categorical_df)
            encoded_df = pd.DataFrame(
                encoded_features,
                columns=self._encoder.get_feature_names_out(CORE_COLUMNS),
            )

            return encoded_df[FEATURES_COLS], data[[target_column]].astype(int)

        else:
            categorical_df = data[CORE_COLUMNS]
            encoded_features = self._encoder.transform(categorical_df)
            encoded_df = pd.DataFrame(
                encoded_features,
                columns=self._encoder.get_feature_names_out(CORE_COLUMNS),
            )
            return encoded_df[FEATURES_COLS]

    def fit(self, features: pd.DataFrame, target: pd.DataFrame) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """
        n_y0 = len(target[target[self._target_column] == 0])
        n_y1 = len(target[target[self._target_column] == 1])
        self._model = LogisticRegression(
            class_weight={1: n_y0 / len(target), 0: n_y1 / len(target)}
        )
        self._model.fit(features, target)

    def predict(self, features: pd.DataFrame) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.

        Returns:
            (List[int]): predicted targets.
        """
        return self._model.predict(features).tolist()

    def save(self):
        """
        Serializes and saves the model and encoder to predefined file paths.
        """
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self._model, f)
        with open(ENCODER_PATH, "wb") as f:
            pickle.dump(self._encoder, f)
