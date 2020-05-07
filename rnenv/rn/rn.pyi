"""
stub file for rn.py
"""

from numpy import ndarray


class RN:
    PERMITTED_PARAMETERS = ...  # type: tuple
    ARRAY_SIZES = ...  # type: tuple
    ARRAY_DIM = ...  # type: int
    PERMITTED_UNITS = ...  # type: tuple

    array = ...  # type: ndarray

    def __init__(self, array: ndarray[int or RN], index: int or RN=1): ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    @property
    def num(self) -> ndarray[int or RN]: return
    @property
    def den(self) -> ndarray[int or RN]: return
    def __validate_array(self, array: ndarray[int or RN]) -> None: ...
    def __validate_den(self, array: ndarray[int or RN]) -> None: ...
    def __validate_array_type(self, array: ndarray[int or RN]) -> None: ...
    def __validate_array_sizes_conformity(self, array: ndarray[int or RN]) -> None: ...
    def __validate_array_data_types(self, array: ndarray[int or RN]) -> None: ...
