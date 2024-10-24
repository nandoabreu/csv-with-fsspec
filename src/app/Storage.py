"""Storage module

This module stores the transformed data
"""
from pandas.core.frame import DataFrame
from fsspec.implementations.local import LocalFileSystem as LocalFS
from adlfs.spec import AzureBlobFileSystem as AzureFS
from s3fs.core import S3FileSystem as S3FS

from .FS import FS


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
        self.file_systems = []

        if local_dir:
            fs = FS().connect(local_dir=local_dir)
            self.file_systems.append((fs, local_dir))

        if all([azure_conn_string_file, azure_container]):
            fs = FS().connect(
                azure_container=azure_container,
                azure_conn_string_file=azure_conn_string_file,
            )
            self.file_systems.append((fs, azure_container))

        if all([aws_secret_file, aws_key]):
            fs = FS().connect(aws_bucket=aws_bucket, aws_secret_file=aws_secret_file, aws_key=aws_key)
            self.file_systems.append((fs, aws_bucket))

    @staticmethod
    def store_csv(df: DataFrame, fs: (LocalFS, AzureFS, S3FS), file_path: str):
        """Store the dataframe as CSV.

        This method will attempt to store the CSV from the dataframe in all available storages.

        Args:
            df (DataFrame): The source dataframe.
            fs (LocalFileSystem, AzureBlobFileSystem, S3FileSystem): The file system object.
            file_path (str): Path to the file to be stored, including the directory, Container or Bucket name.
        """
        with fs.open(file_path, 'w') as f:
            df.to_csv(f, index=False)

        # needs to handle exceptions and report back success or errors
