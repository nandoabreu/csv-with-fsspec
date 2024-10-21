"""Application main file"""
from .config import (
    PROJECT_NAME,
    LOGS_DIR,
    LOG_LEVEL,
    LOG_MAX_ROTATED_FILES,
    LOG_ROTATION_MAX_MB,
    APP_NAME,
    APP_VERSION,
    SOURCE_XML_URL,
    DOWNLOAD_LINK_INDEX,
)
from .Logger import Logger
from .Extractor import Extractor


def main():
    """Application main method or entry point"""
    obj = Logger(
        name=PROJECT_NAME,
        logs_dir=LOGS_DIR,
        log_level=LOG_LEVEL,
        rotated_files=LOG_MAX_ROTATED_FILES,
        rotation_mb=LOG_ROTATION_MAX_MB,
    )
    log = obj.logger

    log.info('{s}- Start {a} v{v} {s}-'.format(s='-*' * 5, a=APP_NAME, v=APP_VERSION))

    extractor = Extractor()
    extractor.fetch_package_url(source_xml_url=SOURCE_XML_URL, link_index=DOWNLOAD_LINK_INDEX)


if __name__ == '__main__':
    main()