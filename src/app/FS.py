from pathlib import Path

import fsspec
from fsspec.implementations.local import LocalFileSystem as LocalFS
from adlfs.spec import AzureBlobFileSystem as AzureFS
from s3fs.core import S3FileSystem as S3FS


class FS:
    """The Filesystem connector

    This class enables and validates connections to different filesystems using the fsspec library.

    Examples:
        > fs = FS().connect(local_dir='data')
        > fs = FS().connect(aws_bucket=aws_bucket, aws_secret_file=aws_secret_file, aws_key=aws_key)
    """

    def __init__(self):
        pass

    def connect(self, **kwargs) -> (LocalFS, AzureFS, S3FS):
        """Connect to a storage system, and validate the connection and location.

        Args (for Local file system):
            local_dir (str): Path to the local directory location.

        Args (for Azure):
            azure_container (str, optional): The container in the Azure Storage.
            azure_conn_string_file (str): The file having the connection string to Azure Storage.

        Args (for AWS):
            aws_bucket (str, optional): The bucket in AWS S3.
            aws_secret_file (str, optional): The file having the secret key to a AWS account.
            aws_key (str, optional): The key to the AWS account.

        Returns:
            (LocalFS, AzureFS, S3FS): A fsspec file system object.

        Raises:
            (ValueError, FileNotFoundError, PermissionError, NotADirectoryError)
        """
        if 'local_dir' in kwargs:
            reference = 'local'
            attrs = {'protocol': 'file'}
            location = kwargs['local_dir']

        elif 'azure_conn_string_file' in kwargs:
            reference = 'azure'
            protected_file = kwargs['azure_conn_string_file']
            protected_data = self._fetch_from_protected_file(protected_file, reference=reference)
            attrs = {'protocol': 'az', 'connection_string': protected_data}
            location = kwargs['azure_container']

        elif 'aws_secret_file' in kwargs:
            reference = 'aws'
            protected_file = kwargs['aws_secret_file']
            protected_data = self._fetch_from_protected_file(protected_file, reference=reference)
            attrs = {'protocol': 's3', 'key': kwargs['aws_key'], 'secret': protected_data}
            location = kwargs['aws_bucket']

        else:
            raise ValueError('File system not recognized')

        fs = fsspec.filesystem(**attrs)
        self._validate_fs_location(filesystem=fs, location=location)

        return fs

    @staticmethod
    def _fetch_from_protected_file(filepath: str, reference: str) -> str:
        """Fetch the content of a protected file

        Args:
            filepath (str): Path to a protected file having a string
            reference (str): One of 'azure' or 'aws'

        Returns:
            (str): A validated string (Azure's connection string, or AWS' secret)

        Raises:
            (FileNotFoundError, PermissionError, ValueError)
        """
        filepath = Path(filepath)

        if not filepath.exists():
            msg = f'Secret file {str(filepath)!r} not found.'
            raise FileNotFoundError(msg)

        if filepath.stat().st_mode & 0o777 != 0o600:
            msg = f'The file {str(filepath)!r} should be protected. I will not use this data.'
            raise PermissionError(msg)

        with open(filepath) as f:
            secret = f.readline().strip()

        if reference == 'azure':
            conn_dict = dict(item.split("=", 1) for item in secret.split(";"))
            if len(conn_dict) < 2 or 'AccountKey' not in conn_dict:
                msg = f'The data fetched from {str(filepath)!r} is not understood as an Azure connection string.'
                raise ValueError(msg)

        elif reference == 'aws':
            if len(secret) < 10:
                msg = f'The data fetched from {str(filepath)!r} is not understood as an AWS secret string.'
                raise ValueError(msg)

        return secret

    @staticmethod
    def _validate_fs_location(filesystem: (LocalFS, AzureFS, S3FS), location: str):
        """Validate a file system storage location.

        This method validates a file system storage and sets the status for this object.
        If the storage location (directory or bucket) does not exist, it attempts to create it.

        Args:
            filesystem (LocalFileSystem, AzureBlobFileSystem, S3FileSystem): The file system object to query.
            location (str): The name to a location to store into (Local directory, Azure container or AWS bucket).
        """
        if 'abfs' in str(filesystem.protocol):
            reference = 'azure'
            expected = 'Container'
        elif 's3' in str(filesystem.protocol):
            reference = 'aws'
            expected = 'Bucket'
        else:
            reference = 'local'
            expected = 'directory'

        try:
            storage_exists = filesystem.exists(location)
        except UserWarning as e:
            if reference == 'azure' and 'Assume it exists' in e:
                storage_exists = None  # Do not trust Azure

        if storage_exists is False:  # Non-existing storage must be created
            # Works for Local and AWS. Azure ignores.
            # Azure seems not to understand a Container as a directory, like Local and AWS do.
            filesystem.makedirs(location)

        elif not filesystem.isdir(location):  # Existing storage (or Azure) must be checked
            raise NotADirectoryError(f'Expected to be a {expected}: {location}')
