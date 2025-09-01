import argparse
import asyncio
import logging
import os
import sys

from pathlib import Path

from app import main


__version__ = "0.0.1a"


sys.path.append(Path(__file__).parent)

DEFAULT_NAME = f"Python/TornadoWeb/MongoClient/{__version__}"
DESCRIPTION = """This is a Python Tornado Web MongoClient HTTP service.

Run the program:
  python3 ./cli.py
  python3 ./cli.py -v --port 8888
"""

if __name__ == "__main__":

    # Arguments
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--port",
        metavar="<int>",
        type=int,
        default=8888,
        help="Set the port to listen for HTTP traffic (default: 8888)",
    )

    ## Database specific arguments
    parser.add_argument(
        "--mongodb",
        metavar="<uri>",
        default=os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017"),
        help="Set the MongoDB URI (Default: mongodb://127.0.0.1:27017) environment variable MONGO_URI",
    )
    parser.add_argument(
        "--username",
        metavar="<str>",
        default=os.environ.get("MONGO_USERNAME"),
        help="Set the MongoDB account username (Default to environment variable MONGO_USERNAME)",
    )
    parser.add_argument(
        "--password",
        metavar="<str>",
        default=os.environ.get("MONGO_PASSWORD"),
        help="Set the MongoDB account password (Default to environment variable MONGO_PASSWORD)",
    )
    parser.add_argument(
        "--database",
        metavar="<str>",
        default=os.environ.get("MONGO_DATABASE", "test"),
        help="Set the MongoDB database (Default to environment variable MONGO_DATABASE or 'test')",
    )
    parser.add_argument(
        "--collection",
        metavar="<str>",
        default=os.environ.get("MONGO_COLLECTION", "test"),
        help="Set the MongoDB document collection (Default to environment variable MONGO_COLLECTION or 'test')",
    )
    parser.add_argument(
        "--default-query-filter",
        metavar="<str>",
        default=os.environ.get("MONGO_QUERY_FILTER", "{}"),
        help='A JSON document that sets default query filter (Default: "{}")',
    )
    parser.add_argument(
        "--default-query-options",
        metavar="<str>",
        default=os.environ.get("MONGO_QUERY_OPTIONS", "{}"),
        help='A JSON document that sets default query options (Default: "{}")',
    )

    parser.add_argument("--version", "-V", action="version", version=DEFAULT_NAME)
    parser.add_argument(
        "--systemd",
        action="store_true",
        default=None,
        help="Run with systemd service mode enabled",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=False,
        help="Run with verbose messages enabled (Default: False)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run with noisy debug messages enabled (Default: False)",
    )
    # Parse all arguments
    argv, remaining_argv = parser.parse_known_args()

    # Pass the program __version__ in as an attribute
    argv.version = __version__

    # Configure logging
    # https://docs.python.org/3/howto/logging.html
    if argv.debug:
        log_level = logging.DEBUG
    elif argv.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S.%f %Z",
        level=log_level,
    )
    logging.debug(f"{__name__} - sys.argv: {sys.argv}")
    logging.debug(f"{__name__} - argv: {argv}")

    # Run the program
    try:
        # Pass all parsed arguments to the main function as key word arguments
        asyncio.run(main(**vars(argv)))
    except KeyboardInterrupt:
        pass
    except Exception as err:
        logging.error(f"{sys.exc_info()[0]}; {err}")
        # Cause the program to exit on error when running in debug mode
        if hasattr(argv, "debug") and argv.debug:
            raise
