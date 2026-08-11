from typing import Tuple

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


def load_data(test_size: float = 0.2, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load the Iris dataset and split into train/test sets.

    Parameters
    ----------
    test_size : float, optional
        Proportion of the dataset to include in the test split (default 0.2).
    random_state : int, optional
        Seed used by the random number generator (default 42).

    Returns
    -------
    X_train, X_test, y_train, y_test : tuple of np.ndarray
        Training and testing feature matrices and target vectors.
    """
    iris = load_iris()
    X, y = iris.data, iris.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test


__all__ = ["load_data"]
