import logging
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Union

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

MODEL = None  # Create model as global variable for enable caching
ENCODER = None  # Create encoder as global variable for enable caching
CURRENT_FOLDER = Path(__file__).parent

MODEL_PATH = CURRENT_FOLDER / "model.pkl"
ENCODER_PATH = CURRENT_FOLDER / "encoder.pkl"

if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
    with open(MODEL_PATH, "rb") as file:
        MODEL = pickle.load(file)
    with open(ENCODER_PATH, "rb") as file:
        ENCODER = pickle.load(file)
else:
    logger.warning("No model or encoder was found")


def get_min_diff(data):
    fecha_o = datetime.strptime(data["Fecha-O"], "%Y-%m-%d %H:%M:%S")
    fecha_i = datetime.strptime(data["Fecha-I"], "%Y-%m-%d %H:%M:%S")
    min_diff = ((fecha_o - fecha_i).total_seconds()) / 60
    return min_diff


class DelayModel:

    def __init__(self):

        self._model = MODEL  # Model should be saved in this attribute.
        self._encoder = ENCODER
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

        if target_column:
            # Setup target column
            data["min_diff"] = data.apply(get_min_diff, axis=1)
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
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self._model, f)
        with open(ENCODER_PATH, "wb") as f:
            pickle.dump(self._encoder, f)
