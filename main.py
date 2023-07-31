#!/bin/python3
# coding=utf-8

from banking.api import app as bankingapi
import logging
import os

logging.basicConfig(
    format=os.getenv(
        "LOGFORMAT", "[%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
    ),
    level=os.getenv("LOGLEVEL", "WARNING"),
    force=True,
)


if __name__ == "__main__":
    os.environ["PERSISTENCE_MODULE"] = "eventsourcing.sqlite"
    os.environ["SQLITE_DBNAME"] = "accounts.sqlite"
    bankingapi.run(debug=True)
