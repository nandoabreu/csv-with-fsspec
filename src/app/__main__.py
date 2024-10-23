"""Application main file"""
from datetime import datetime as _dt
from requests.exceptions import ConnectionError, HTTPError

from .config import (
    PROJECT_NAME,
    LOGS_DIR,
    LOG_LEVEL,
    LOG_MAX_ROTATED_FILES,
    LOG_ROTATION_MAX_MB,
    ENABLE_STDOUT_LOG,
    APP_NAME,
    APP_VERSION,
    SOURCE_XML_URL,
    DOWNLOAD_LINK_INDEX,
    STORAGE_LOCAL_DIR,
)
from .Logger import Logger
from .Extractor import Extractor
from .Transformer import Transformer
from .Storage import Storage


def main():
    """Application main method or entry point"""
    obj = Logger(
        name=PROJECT_NAME,
        logs_dir=LOGS_DIR,
        log_level=LOG_LEVEL,
        rotated_files=LOG_MAX_ROTATED_FILES,
        rotation_mb=LOG_ROTATION_MAX_MB,
        enable_stdout_logs=ENABLE_STDOUT_LOG,
    )
    log = obj.logger
    log.info('{s}- Start {a} v{v} {s}-'.format(s='-*' * 5, a=APP_NAME, v=APP_VERSION))

    extractor = Extractor()

    try:
        package_url = extractor.fetch_package_url(source_xml_url=SOURCE_XML_URL, link_index=DOWNLOAD_LINK_INDEX)

    except (ConnectionError, HTTPError) as e:
        log.error('Could not fetch file - Update the SOURCE_XML_URL var in env.toml and/or .env. See logs for details.')
        log.debug(e)

    log.debug(f'Parse data from {package_url=}')
    df = extractor.parse_package_content(package_url=package_url)
    log.info(f'Parsed {len(df)} data record(s)')

    Transformer().create_derived_columns(df)

    storage = Storage(
        local_dir=STORAGE_LOCAL_DIR,
    )

    has_valid_storage = False
    for storage_ref, status in storage.status.items():
        if not status['valid']:
            if status['error'] != 'value not set':
                log.error('Storage not enabled for {!r}: {}'.format(storage_ref, status['error']))
            continue

        has_valid_storage = True

    if not has_valid_storage:
        log.error('No storage enabled')
        return

    filename = 'data.{}Z.csv'.format(_dt.utcnow().strftime('%Y%m%d-%H%M'))
    log.info(f'Request storage as file: {filename}')
    errors = storage.store_csv(df=df, file_name=filename)

    for storage_ref, error in errors.items():
        log.error(f'Unable to store in {storage_ref!r}: {error}')


if __name__ == '__main__':
    main()
