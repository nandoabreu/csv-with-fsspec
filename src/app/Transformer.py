"""Transformer module

This module handles transformation of data
"""
from numpy import where
from pandas.core.frame import DataFrame


class Transformer:
    def __init__(self):
        pass

    @staticmethod
    def create_derived_columns(df: DataFrame):
        """Create derived columns from existing ones

        This method updates the provided pandas DataFrame by adding two new columns:
        - `a_count`: counting occurrences of the lower-case char "a" in "FullNm"
        - `contains_a`: set to "YES" if `a_count` is greater than 0, otherwise "NO"

        Args:
            df (DataFrame): The pandas DataFrame to be updated

        Returns:
            None: The DataFrame is modified in place, so there is no need to return it
        """
        df['a_count'] = df['FullNm'].str.count('a').fillna(0)
        df['contains_a'] = where(df['a_count'] > 0, 'YES', 'NO')
