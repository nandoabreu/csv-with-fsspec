"""Storage module

This module stores the transformed data
"""
from pathlib import Path

import fsspec
from pandas.core.frame import DataFrame


class Storage:
    def __init__(self, local_dir: str = None, azure_conn_string_file: str = None, azure_container: str = None):
        """Initialize Storage with the provided destinations

        If a destination is not valid, it will be skipped. If no destination is valid,
        an error will be raised.

        Args:
            local_dir (str): Local file destination path
            azure_conn_string_file (str): The file having the connection string to Azure Storage
            azure_container (str): The container in the Azure Storage
        """
        self.__status = {}

        self.local_dir = Path(local_dir) if local_dir else None
        self.validate_local_path()

        self.azure_container = azure_container if azure_conn_string_file else None
        self.__azure_conn_str = None
        self.set_connection_string_from_file(filepath=azure_conn_string_file)
        self.__azure_storage = None
        self.validate_azure_storage()
        # fsspec.filesystem('az', connection_string=self.connection_string

    @property
    def status(self) -> dict:
        """Fetch the statuses for the initialized storages

        Returns:
            dict: As in {'local': {'valid': True, 'error': (str, None)}}
        """
        return self.__status

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
            file_path = Path(f'{self.local_dir}/{file_name}')

            try:
                df.to_csv(file_path, index=False)
            except OSError as e:
                errors['local'] = str(e)

        if self.status.get('azure', {}).get('valid', False):
            file_path = f"{self.azure_container}/{file_name}"
            with self.__azure_storage.open(file_path, 'w') as f:
                df.to_csv(f, index=False)
            print(f"Data stored in Azure Blob Storage at: {file_path}")

        return errors

    def set_connection_string_from_file(self, filepath: str):
        """TBD"""
        if not filepath:
            return

        filepath = Path(filepath)
        if filepath.stat().st_mode & 0o777 != 0o600:
            return f'The file {str(filepath)!r} should be protected. I will not use this data.'

        with open(filepath) as f:
            conn_str = f.readline().strip()
            conn_dict = dict(item.split("=", 1) for item in conn_str.split(";"))

            if len(conn_dict) < 2 or 'AccountKey' not in conn_dict:
                return f'The data fetched from {str(filepath)!r} is not understood as an Azure connection string.'

            self.__azure_conn_str = conn_str

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

    def validate_azure_storage(self) -> None:
        """Validate Azure storage data set with init"""
        status = {'storage_ref': 'azure', 'error': None}

        if not self.__azure_conn_str:
            status['error'] = 'connection not set'

        elif not self.azure_container:
            status['error'] = 'container not set'

        else:
            self.__azure_storage = fsspec.filesystem('az', connection_string=self.__azure_conn_str)
            if self.azure_container not in self.__azure_storage.ls('/'):
                status['error'] = 'container not in storage'

        print(f'update {self.__status=}')
        self.__set_status(**status)

    def __set_status(self, storage_ref: str, error: str = None):
        self.__status.update({
            storage_ref: {
                'valid': False if error else True,
                'error': error,
            },
        })
