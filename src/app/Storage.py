"""Storage module

This module stores the transformed data
"""
from pathlib import Path

import fsspec
from pandas.core.frame import DataFrame


class Storage:
    def __init__(
            self,
            local_dir: str = None,
            azure_conn_string_file: str = None,
            azure_container: str = None,
            aws_secret_file: str = None,
            aws_key: str = None,
            aws_bucket: str = None,
    ):
        """Initialize Storage with the provided destinations

        Args:
            local_dir (str, optional): Local file destination path
            azure_conn_string_file (str, optional): The file having the connection string to Azure Storage
            azure_container (str, optional): The container in the Azure Storage
            aws_secret_file (str, optional): The file having the secret key to a AWS account
            aws_key (str, optional): The key to the AWS account
            aws_bucket (str, optional): The bucket in AWS S3
        """
        self.__status = {}

        self.local_dir = Path(local_dir) if local_dir else None
        self.validate_local_path()

        self.__azure_storage = None
        self.__azure_conn_str = None
        self.azure_container = None
        if all([azure_conn_string_file, azure_container]):
            self.fetch_from_protected_file(azure_conn_string_file, reference='azure')
            self.azure_container = azure_container
        self.validate_azure_storage()

        self.__aws_storage = None
        self.__aws_key = None
        self.__aws_secret = None
        self.aws_bucket = None
        if all([aws_secret_file, aws_key]):
            self.fetch_from_protected_file(aws_secret_file, reference='aws')
            self.__aws_key = aws_key
            self.aws_bucket = aws_bucket
        self.validate_aws_account()

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

        if self.status.get('aws', {}).get('valid', False):
            file_path = f"{self.aws_bucket}/{file_name}"
            with self.__aws_storage.open(file_path, 'w') as f:
                df.to_csv(f, index=False)
            print(f"Data stored in AWS at: {file_path}")

        return errors

    def fetch_from_protected_file(self, filepath: str, reference: str):
        """TBD"""
        if not filepath:
            return

        filepath = Path(filepath)
        if filepath.stat().st_mode & 0o777 != 0o600:
            return f'The file {str(filepath)!r} should be protected. I will not use this data.'

        with open(filepath) as f:
            conn_str = f.readline().strip()

        if reference == 'azure':
            conn_dict = dict(item.split("=", 1) for item in conn_str.split(";"))
            if len(conn_dict) < 2 or 'AccountKey' not in conn_dict:
                return f'The data fetched from {str(filepath)!r} is not understood as an Azure connection string.'

            self.__azure_conn_str = conn_str

        elif reference == 'aws':
            if len(conn_str) < 10:
                return f'The data fetched from {str(filepath)!r} is not understood as an AWS secret string.'

            self.__aws_secret = conn_str

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

        self.__set_status(**status)

    def validate_aws_account(self) -> None:
        """Validate AWS account data set with init"""
        status = {'storage_ref': 'aws', 'error': None}

        if not self.__aws_key:
            status['error'] = 'key not set'

        elif not self.__aws_secret:
            status['error'] = 'secret not set'

        elif not self.aws_bucket:
            status['error'] = 'bucket not set'

        else:
            self.__aws_storage = fsspec.filesystem('s3', key=self.__aws_key, secret=self.__aws_secret)
            try:
                self.__aws_storage.ls(self.aws_bucket)
            except FileNotFoundError:
                status['error'] = 'bucket not in storage'
            except PermissionError:
                status['error'] = 'access denied to bucket'

        self.__set_status(**status)

    def __set_status(self, storage_ref: str, error: str = None):
        self.__status.update({
            storage_ref: {
                'valid': False if error else True,
                'error': error,
            },
        })
