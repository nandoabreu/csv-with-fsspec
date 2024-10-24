# csv-with-fsspec

Load CSV, transform using Pandas, store via pandas and fsspec

This project loads a zip file from a remote location, unpacking and transforming
its content using Pandas and other Python dependencies. After data transformation,
a CSV file is stored locally, or in Azure. See the [Setup](#setup) chapter
to enable different storages.


## Setup

The [env.toml](env.toml) file must be updated to enable several settings. The basic ones are here explained:

```
SOURCE_XML_URL (str): The URL for the first XML to be fetched. The ZIP file will be fetched from this XML.
DOWNLOAD_LINK_INDEX (int): The index be used to find the URL to the ZIP file inside the first XML.

STORAGE_LOCAL_DIR (str): Relative or absolute path to store the CSV file. If the directory does not exit, it will be created.

STORAGE_AZURE_CONNECTION_STRING_FILEPATH (str): Path to a file having an Azure Blob connection string. This file must be in mode 600 (rw,-,-)
STORAGE_AZURE_CONTAINER_NAME (str): Name of the container to store the CSV file.

STORAGE_AWS_SECRET_FILEPATH (str): Path to a file having an AWS connection secret. This file must be in mode 600 (rw,-,-)
STORAGE_AWS_KEY_STRING (str): The key to the AWS account.
STORAGE_AWS_BUCKET_NAME (str): Name of the bucket to store the CSV file.

ENABLE_STDOUT_LOG (bool): Higher-level logs can be printed to stdout. This is ideal in case this App runs as a systemctl daemon.
```

### Developer setup

> Note: in case your system does not use make, please open the [Makefile](Makefile) and run each command
> manually from the targets here listed.

```shell
make env-setup
```


## Run the App

> Note: refer to [Setup](#setup) before running the App

```shell
make run
```

A sample output of this run can be found in
[tests/samples/data.20241024-1537Z.csv](tests/samples/data.20241024-1537Z.csv).


## Reports

### Local storage

```shell
data/
├── data.20241023-1431Z.csv
├── data.20241023-1655Z.csv
└── data.20241023-1656Z.csv
```

### Azure storage

![](docs/azure.png)

### AWS S3

![](docs/awss3.png)

### Logs

```
{"cid": null, "ts": "2024-10-24 15:37:57,995", "log": "DEBUG", "msg": "RotatingFileHandler logs set to log from the DEBUG level"},
{"cid": null, "ts": "2024-10-24 15:37:57,996", "log": "DEBUG", "msg": "StreamHandler logs set to log from the INFO level"},
{"cid": null, "ts": "2024-10-24 15:37:57,996", "log": "INFO", "msg": "Logs will be stored in UTC timezone at /tmp/logs/csv-with-fsspec.log"},
{"cid": null, "ts": "2024-10-24 15:37:57,996", "log": "DEBUG", "msg": "I will rotate 9 log files, at 9437184 bytes"},
{"cid": null, "ts": "2024-10-24 15:37:57,996", "log": "INFO", "msg": "-*-*-*-*-*- Start CSV with fsspec v0.2.0 -*-*-*-*-*-"},
{"cid": null, "ts": "2024-10-24 15:37:58,249", "log": "DEBUG", "msg": "Parse data from package_url='http://0.0.0.0:8888/data.xml.zip'"},
{"cid": null, "ts": "2024-10-24 15:37:58,273", "log": "INFO", "msg": "Parsed 3 data record(s)"},
{"cid": null, "ts": "2024-10-24 15:37:59,276", "log": "INFO", "msg": "Request storage for: data.20241024-1537Z.csv"},
{"cid": null, "ts": "2024-10-24 15:37:59,276", "log": "INFO", "msg": "Request ('file', 'local') storage"},
{"cid": null, "ts": "2024-10-24 15:37:59,280", "log": "INFO", "msg": "Request abfs storage"},
{"cid": null, "ts": "2024-10-24 15:37:59,448", "log": "INFO", "msg": "Request ('s3', 's3a') storage"},
```

## todo's

- [ ] Unit test Extractor.parse_package_content
- [ ] Fully unit test FS (file system connector) (mocking the connections)
- [ ] Find a way to cancel the Azure tests in case the connection fails (thread timeout was tried)
- [ ] Allow Azure/AWS storage in directories inside the Container/Bucket
- [ ] This 0.2 version need more exception handling
- [ ] Needs better loging for each file system successful storage
