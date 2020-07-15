"""
Script to download OperationType and Library definitions from the aquarium instance
identified in the resources.py file.
"""

import argparse
import logging
import instance
import category
import operation_type
import library
import os
import sys

from config import (
    add_config,
    set_default_instance
)
from paths import (
    create_named_path
)
from session import create_session

logging.basicConfig(level=logging.INFO)


def main():
    parser = get_argument_parser()
    args = parser.parse_args()
    # call the function determined by the arguments
    try:
        args.func(args)
    except AttributeError:
        parser.print_help(sys.stderr)


def get_argument_parser():
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

    parser_test = subparsers.add_parser("test")
    add_code_arguments(parser_test, action="test")
    parser_test.set_defaults(func=do_test)

    return parser


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
        required=(action == 'create' or action == 'push' or action == 'test')
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
        operation_type.create(aq, path, args.category, args.operation_type)
        operation_type.get_operation_type(
            aq, path, args.category, args.operation_type)
        return

    if args.library:
        # TODO: implement create library
        logging.error("Creating library currently not implemented")
        return


def do_pull(args):
    aq = create_session(path=config_path())
    path = os.path.normpath(args.directory)

    if not args.category:
        instance.pull(session=aq, path=path)
        return

    # have category, check for a library or operation type
    if args.library:
        library.get_library(aq, path, args.category, args.library)
        return

    if args.operation_type:
        operation_type.get_operation_type(
            aq, path, args.category, args.operation_type)
        return

    # get whole category
    category.pull_category(aq, path, args.category)


def do_push(args):
    aq = create_session(path=config_path())
    path = os.path.normpath(args.directory)

    if not args.category:
        instance.push(session=aq, path=path)
        return

    category_path = create_named_path(path, args.category)

    if args.library:
        library.select_library(aq, category_path, args.library)
        return

    if args.operation_type:
        operation_type.select_operation_type(
            aq, category_path, args.operation_type)
        return

    category.select_category(aq, category_path)


def do_test(args):
    aq = create_session(path=config_path())
    path = os.path.normpath(args.directory)

    if not args.category:
        instance.run_test(session=aq, path=path)
        return

    category_path = create_named_path(path, args.category)

    if args.library:
        # TODO: should push and then run test
        library.run_test(
            session=aq,
            path=category_path,
            name=args.library
        )
        return

    if args.operation_type:
        # TODO: should push and then run test
        operation_type.run_test(
            session=aq,
            path=category_path,
            name=args.operation_type
        )
        return

    category.run_test(session=aq, path=category_path)


if __name__ == "__main__":
    main()
