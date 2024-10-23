# csv-with-fsspec

Load CSV, transform using Pandas, store via pandas and fsspec

This project loads a zip file from a remote location, unpacking and transforming
its content using Pandas and other Python dependencies. After data transformation,
a CSV file is stored locally, or in Azure. See the [Setup](#setup) chapter
to enable different storages.


## Developer setup

> Note: in case your system does not use make, please open the [Makefile](Makefile) and run each command
> manually from the targets here listed.

```shell
make env-setup
```

## Setup

The [env.toml](env.toml) file must be updated to enable several settings. The basic ones are here explained:

```shell
SOURCE_XML_URL (str): The URL for the first XML to be fetched. The ZIP file will be fetched from this XML.
DOWNLOAD_LINK_INDEX (int): The index be used to find the URL to the ZIP file inside the first XML.

STORAGE_LOCAL_DIR (str): Relative or absolute path to store the CSV file. If the directory does not exit, it will be created.

STORAGE_AZURE_CONNECTION_STRING_FILEPATH (str): Path to a file having an Azure Blob connection string. This file must be in mode 600 (rw,-,-)
STORAGE_AZURE_CONTAINER_NAME (str): Name of the container to store the CSV file.

ENABLE_STDOUT_LOG (bool): Higher-level logs can be printed in std. This is ideal in case this App runs as a systemctl daemon.
```


## todo's

- [ ] Unit test Extractor.parse_package_content
- [ ] Fully unit test Storage with azure connection (mocking the connection)
- [ ] Find a way to cancel the Azure tests in case the connection fails (thread timeout was tried)
