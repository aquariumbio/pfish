"""
Script to download OperationType and Library files from
the configured aquarium instance
"""

import argparse
import logging
import os
import sys
import instance
import category
import operation_type
import library

from config import (
    add_config,
    set_default_instance,
    show_config
)
from paths import (
    create_named_path
)
from session import create_session

logging.basicConfig(level=logging.INFO)


def main():
    """call the function determined by the arguments"""
    parser = get_argument_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help(sys.stderr)


def get_argument_parser():
    parser = argparse.ArgumentParser(
        description="Create, push, pull, and test Aquarium protocols")

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
        help="the URL for the aquarium instance",
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

    parser_show = config_subparsers.add_parser(
        "show",
        help="show all configurations"
    )

    parser_show.set_defaults(func=do_config_show)

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
        help="working directory for the command, default is current directory",
        default=os.getcwd()
    )
    parser.add_argument(
        "-n", "--name",
        help="login configuration name, default is 'local'",
        default="local"
    )
    parser.add_argument(
        "-c", "--category",
        help="category of the operation type or library",
        # TODO: Do we want to require a category for testing?
        required=(action == 'create' or action == 'test')
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
    return os.path.normpath(
        os.path.join(os.environ.get('SCRIPT_DIR'), 'config')
    )


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


def do_config_show(args):
    show_config(path=config_path())


def do_create(args):
    session = create_session(path=config_path())
    path = os.path.normpath(args.directory)

    if args.category:

        if args.operation_type:
            operation_type.create(
                session=session, path=path,
                category=args.category,
                name=args.operation_type)
            operation_type.pull(
                session=session, path=path,
                category=args.category,
                name=args.operation_type)
            return

        if args.library:
            library.create(
                session=session, path=path,
                category=args.category,
                name=args.library)
            library.pull(
                session=session, path=path,
                category=args.category,
                name=args.library)
            return

        logging.error(
            "To create an operation type or library, you must enter a name.")


def do_pull(args):
    """
    Call appropriate pull function based on arguments
    Default is to pull everything from the instance
    """
    session = create_session(path=config_path())
    path = os.path.normpath(args.directory)

    if args.category:
        if args.library:
            library.pull(
                session=session, path=path,
                category=args.category, name=args.library)
            return

        if args.operation_type:
            operation_type.pull(
                session=session, path=path,
                category=args.category, name=args.operation_type)
            return

        category.pull(session=session, path=path, name=args.category)
        return

    if args.library or args.operation_type:
        logging.error(
            "To pull an operation type or library, you must enter a category")
        return

    instance.pull(session=session, path=path)
    return


def do_push(args):
    session = create_session(path=config_path())
    path = os.path.normpath(args.directory)

    # TODO: Shouldn't need category, because you can get it from the definition file
    if args.category:
        category_path = create_named_path(path, args.category)
        if args.library:
            library.push(
                session=session,
                path=create_named_path(
                    category_path, args.library, subdirectory="libraries")
            )
            return

        if args.operation_type:
            operation_type.push(
                session=session,
                path=create_named_path(
                    category_path, args.operation_type,
                    subdirectory="operation_types")
            )
            return

        category.push(session=session, path=category_path)

    if args.library or args.operation_type:
        logging.error(
            "To test a single operation type or library, you must enter a category")
        return

    instance.push(session=session, path=path)


def do_test(args):
    session = create_session(path=config_path())
    path = os.path.normpath(args.directory)

    # have category, check for a library or operation type
    if args.category:
        category_path = create_named_path(path, args.category)
        if args.library:
            library.run_test(
                session=session,
                path=create_named_path(
                    category_path, args.operation_type,
                    subdirectory="libraries"),
                category=args.category,
                name=args.library
            )
            return

        if args.operation_type:
            operation_type.run_test(
                session=session,
                path=create_named_path(
                    category_path, args.operation_type,
                    subdirectory="operation_types"),
                category=args.category,
                name=args.operation_type
            )
            return

        category.run_tests(
            session=session, path=category_path, name=args.category)
        return

    if args.library or args.operation_type:
        logging.error(
            "To test a single operation type or library, you must enter a category")
        return

    instance.run_tests(session=session, path=path)


if __name__ == "__main__":
    main()
