"""
Script to download OperationType definitions from the aquarium instance
identified in the resources.py file.
"""

import os
import argparse
import logging
from pull import (
    get_all,
    get_category,
    get_library,
    get_operation_type
)
from push import (
    create_new_operation_type,
    select_library,
    select_operation_type,
    select_category
)
from paths import (
    create_named_path,
    makedirectory
)
from resources import resources
from pydent import AqSession

logging.basicConfig(level=logging.INFO)


def open_aquarium_session():
    """
    Starts Aquarium Session
    """
    aq = AqSession(
        resources['aquarium']['login'],
        resources['aquarium']['password'],
        resources['aquarium']['url']
    )
    return aq


def main():
    parser = argparse.ArgumentParser(
        description="Pull or Push files from/to Aquarium. Create new operation types")
    parser.add_argument(
        "action",
        choices=["push", "pull", "create"],
        help="whether to push or pull Operation Type and/or Library files, or to create a new OperationType"
    )
    parser.add_argument(
        "-d", "--directory",
        help="directory for reading or writing files. Created if does not already exist",
        default=os.getcwd()
    )
    parser.add_argument(
        "-c", "--category",
        help="category of the operation type or library"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--library", help="the library to pull")
    group.add_argument(
        "-o", "--operation_type",
        help="the operation type to pull"
    )

    args = parser.parse_args()

    aq = open_aquarium_session()

    path = os.path.normpath(args.directory)
    makedirectory(path)

    if args.action == 'pull':
        if not args.category:
            if args.library:
                logging.error("Category required to pull library")
                return

            if args.operation_type:
                logging.error("Category required to pull operation type")
                return

            # no category, library or operation type
            get_all(aq, path)
            return

        # have category, check for a library or operation type
        if args.library:
            get_library(aq, path, args.category, args.library)
            return

        if args.operation_type:
            get_operation_type(aq, path, args.category, args.operation_type)
            return

        # get whole category
        get_category(aq, path, args.category)
        return

    # action was not pull, should be push or create
    if args.action != 'push' and args.action != 'create':
        logging.warning("Expected an action")
        return


    # action is push or create
    if not args.category:
        logging.error('Category is required for push and create')
        return

    # have category, look for library or operation type
    category_path = create_named_path(path, args.category)

    user_id = aq.User.where({"login": aq.login}) 
    
    if args.action == 'create' and args.operation_type:
        create_new_operation_type(aq, path, args.category, args.operation_type)
        get_operation_type(aq, path, args.category, args.operation_type)
        return

    if args.library:
        select_library(aq, user_id, category_path, args.library)
        return

    if args.operation_type:
        select_operation_type(aq, user_id, category_path, args.operation_type)
        return
    
    select_category(aq, user_id, category_path)


if __name__ == "__main__":
    main()
