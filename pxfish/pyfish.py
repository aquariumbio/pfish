"""
Script to download OperationType definitions from the aquarium instance
identified in the resources.py file.
"""

import os
import argparse
import logging
from config import (
    add_config,
    set_default_instance
)
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
from session import create_session

logging.basicConfig(level=logging.INFO)


def main():
    args = get_arguments()
    # call the function determined by the arguments
    args.func(args)


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Create, push and pull Aquarium protocols")

    # Create parsers for subcommands
    subparsers = parser.add_subparsers(title="subcommands")

    parser_create = subparsers.add_parser("create")
    add_code_arguments(parser_create, action="create")
    parser_create.set_defaults(func=do_create)

    parser_config = subparsers.add_parser("configure")
    config_subparsers = parser_config.add_subparsers()
    parser_add = config_subparsers.add_parser(
        "add",
        help="Add/update login configuration"
    )
    parser_add.add_argument(
        '-n', "--name",
        help="the name to use for the aquarium instance",
        default="local"
    )
    parser_add.add_argument(
        "-l", "--login",
        help="the login name for the aquarium instance",
        default="neptune"
    )
    parser_add.add_argument(
        "-p", "--password",
        help="the password for the login",
        default="aquarium"
    )
    parser_add.add_argument(
        "-u", "--url",
        help="the URL for the aquarim instance",
        default="http://localhost/"
    )
    parser_add.set_defaults(func=do_config_add)

    parser_default = config_subparsers.add_parser(
        "set-default",
        help="set default login configuration"
    )
    parser_default.add_argument(
        '-n',
        '--name',
        help="the name of the default login configuration",
        default="local"
    )
    parser_default.set_defaults(func=do_config_default)

    parser_pull = subparsers.add_parser("pull")
    add_code_arguments(parser_pull, action="pull")
    parser_pull.set_defaults(func=do_pull)

    parser_push = subparsers.add_parser("push")
    add_code_arguments(parser_push, action="push")
    parser_push.set_defaults(func=do_push)

    args = parser.parse_args()
    return args


def add_code_arguments(parser, *, action):
    parser.add_argument(
        "-d", "--directory",
        help="working directory for the command",
        default=os.getcwd()
    )
    parser.add_argument(
        "-n", "--name",
        help="login configuration name",
        default="local"
    )
    parser.add_argument(
        "-c", "--category",
        help="category of the operation type or library",
        required=(action == 'create' or action == 'push')
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-l", "--library",
        help="the library to {}".format(action)
    )
    group.add_argument(
        "-o", "--operation_type",
        help="the operation type to {}".format(action)
    )


def config_path():
    return os.path.normpath('/script/config')


def do_config_add(args):
    add_config(
        path=config_path(),
        key=args.name,
        login=args.login,
        password=args.password,
        url=args.url
    )


def do_config_default(args):
    set_default_instance(config_path(), name=args.name)


def do_create(args):
    aq = create_session(path=config_path())
    path = os.path.normpath(args.directory)

    if args.operation_type:
        create_new_operation_type(aq, path, args.category, args.operation_type)
        get_operation_type(aq, path, args.category, args.operation_type)
        return

    if args.library:
        # TODO: implement create library
        pass


def do_pull(args):
    aq = create_session(path=config_path())
    path = os.path.normpath(args.directory)

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


def do_push(args):
    aq = create_session(path=config_path())
    path = os.path.normpath(args.directory)

    category_path = create_named_path(path, args.category)
    if args.library:
        select_library(aq, category_path, args.library)
        return

    if args.operation_type:
        select_operation_type(aq, category_path, args.operation_type)
        return

    select_category(aq, category_path)


if __name__ == "__main__":
    main()
