"""Storage module

This module stores the transformed data
"""
from pathlib import Path

from pandas.core.frame import DataFrame


class Storage:
    def __init__(self, local_dir: str = None):
        """Initialize Storage with the provided destinations

        If a destination is not valid, it will be skipped. If no destination is valid,
        an error will be raised.

        Args:
            local_dir (str): Local file destination path
        """
        self.local_dir = Path(local_dir) if local_dir else None

        self.__status = {}
        self.validate_local_path()

    def store_csv(self, df: DataFrame, file_name: str) -> dict:
        """Store the dataframe as CSV in available storages

        Args:
            df (DataFrame): The source dataframe
            file_name (str): Name of the file to store

        Returns:
            dict: Having one error message per destination, or empty if no error
        """
        errors = {}

        if self.status.get('local', {}).get('valid', False):
            local_path = Path(f'{self.local_dir}/{file_name}')

            try:
                df.to_csv(local_path, index=False)
            except OSError as e:
                errors['local'] = str(e)

        return errors

    @property
    def status(self) -> dict:
        """Fetch the statuses for the initialized storages

        Returns:
            dict: As in {'local': {'valid': True, 'error': (str, None)}}
        """
        return self.__status

    def validate_local_path(self) -> None:
        """Validate a local directory set with init"""
        status = {'storage_ref': 'local', 'error': None}

        if not self.local_dir:
            status['error'] = 'directory not set'

        elif not self.local_dir.exists():
            self.local_dir.mkdir(parents=True)

        elif not self.local_dir.is_dir():
            status['error'] = 'not a directory'

        else:
            try:
                t = self.local_dir / 'writeable.tmp'
                t.touch()
                t.unlink()

            except PermissionError:
                status['error'] = 'could not write in directory'

        self.__set_status(**status)

    def __set_status(self, storage_ref: str, error: str = None):
        self.__status.update({
            storage_ref: {
                'valid': False if error else True,
                'error': error,
            },
        })
