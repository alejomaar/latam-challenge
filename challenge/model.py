from datetime import datetime
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle

import os
import logging

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,  # Capture all logging levels
    format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",  # Optional: Set a custom date format
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


MODEL = None  # Create model as global variable for enable caching
MODEL_PATH = "challenge/model.pkl"

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as file:
        MODEL = pickle.load(file)
else:
    logger.warning("No model was found")


def get_min_diff(data):
    fecha_o = datetime.strptime(data["Fecha-O"], "%Y-%m-%d %H:%M:%S")
    fecha_i = datetime.strptime(data["Fecha-I"], "%Y-%m-%d %H:%M:%S")
    min_diff = ((fecha_o - fecha_i).total_seconds()) / 60
    return min_diff


class DelayModel:

    def __init__(self):

        self._model = MODEL  # Model should be saved in this attribute.
        self._target_column = None

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

        features = pd.concat(
            [
                pd.get_dummies(data["OPERA"], prefix="OPERA"),
                pd.get_dummies(data["TIPOVUELO"], prefix="TIPOVUELO"),
                pd.get_dummies(data["MES"], prefix="MES"),
            ],
            axis=1,
        )
        features = features[FEATURES_COLS]
        if target_column:
            data["min_diff"] = data.apply(get_min_diff, axis=1)
            data[target_column] = np.where(
                data["min_diff"] > THRESHOLD_IN_MINUTES, 1, 0
            )
            self._target_column = target_column

            return features[FEATURES_COLS], data[[target_column]].astype(int)

        else:
            return features

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

    def save(self, filename="model.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self._model, f)
