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
    """Calls the function determined by the arguments"""
    parser = get_argument_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help(sys.stderr)


def get_argument_parser():
    """
    Creates parser and subparsers for subcommands
    Subparsers: create, push, pull, test, config
    """
    parser = argparse.ArgumentParser(
        description="Create, push, pull, and test Aquarium protocols")

    subparsers = parser.add_subparsers(title="subcommands")

    parser_config = subparsers.add_parser("configure")

    config_subparsers = parser_config.add_subparsers()

    parser_add = config_subparsers.add_parser(
        "add",
        help="Add/update login configuration"
    )

    add_config_arguments(parser_add)

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
        'show',
        help='show all configurations'
    )

    parser_show.set_defaults(func=do_config_show)

    parser_pull = subparsers.add_parser("pull")
    add_code_arguments(parser_pull, action="pull")
    parser_pull.set_defaults(func=do_pull)

    parser_push = subparsers.add_parser("push")
    add_code_arguments(parser_push, action="push")
    parser_push.set_defaults(func=do_push)

    parser_create = subparsers.add_parser("create")
    add_code_arguments(parser_create, action="create")
    parser_create.set_defaults(func=do_create)

    parser_test = subparsers.add_parser("test")
    add_code_arguments(parser_test, action="test")
    parser_test.set_defaults(func=do_test)

    return parser


def add_config_arguments(parser):
    """Adds optional args for configuration subparser"""
    parser.add_argument(
        '-n', "--name",
        help="the name to use for the aquarium instance",
        default="local"
    )
    parser.add_argument(
        "-l", "--login",
        help="the login name for the aquarium instance",
        default="neptune"
    )
    parser.add_argument(
        "-p", "--password",
        help="the password for the login",
        default="aquarium"
    )
    parser.add_argument(
        "-u", "--url",
        help="the URL for the aquarium instance",
        default="http://localhost/"
    )


def add_code_arguments(parser, *, action):
    """Adds optional arguments for code subparsers"""
    parser.add_argument(
        "-a", "--all",
        help="push or pull all files in a directory",
        action="store_true"
    )

    parser.add_argument(
        "-d", "--directory",
        help="working directory for the command. optional for Pull (default is current directory). Required for push",
        required=(action == 'push'),
        default=os.getcwd()
    )

    parser.add_argument(
        "-n", "--name",
        help="login configuration name",
        type=str
    )

    parser.add_argument(
        "-c", "--category",
        help="category of the operation type or library",
        required=(action == 'create')
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

    if action == 'push':
        parser.add_argument(
            '-f', '--force',
            help='overwrite existing instance field types with data from definition file',
            #default=False,
            action="store_true"
            )

    if action == 'test':
        parser.add_argument(
            "-t", "--timeout",
            help="timeout (seconds) for running test",
            type=int,
            default=None
        )


def config_path():
    return os.path.normpath(
        os.path.join(os.environ.get('SCRIPT_DIR'), 'config')
    )


def do_config_add(args):
    """Adds new configuration"""
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
    """
    Calls appropriate create function based on arguments
    """
    session = create_session(path=config_path(), name=args.name)
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
    Calls appropriate pull function based on arguments
    """
    session = create_session(path=config_path(), name=args.name)
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
            'To pull an operation type or library, you must enter a category')
        return

    if args.all:
        instance.pull(session=session, path=path)
        return

    logging.error(
        'You must choose either a category, library, or operation type to pull. Or use -a or --all to pull all files in an instance'
        )

def do_push(args):
    """
    Calls appropriate push function based on arguments
    """
    session = create_session(path=config_path(), name=args.name)
    path = os.path.normpath(args.directory)

    if args.force and not args.operation_type:
        logging.warning('Force Flag only operates with a single Operation Type')
        return
    
    # TODO: get category from the definition file
    if args.category:
        category_path = create_named_path(path, args.category)
        if args.library:
            library.push(
                session=session,
                path=create_named_path(
                    category_path, args.library, subdirectory='libraries')
            )
            return

        if args.operation_type:
            operation_type.push(
                session=session,
                path=create_named_path(
                    category_path, args.operation_type,
                    subdirectory='operation_types'),
                force=args.force
            )
            return

        category.push(session=session, path=category_path)
        return

    if args.library or args.operation_type:
        logging.error(
            'To push a single operation type or library, you must enter a category')
        return

    if args.all:
        instance.push(session=session, path=path)
        return

    logging.error(
        'You must choose either a category, library, or operation type to push. Or use -a or --all to push an entire directory'
        )
    return


def do_test(args):
    """
    Calls appropriate test function based on arguments
    """
    session = create_session(path=config_path(), name=args.name)
    path = os.path.normpath(args.directory)

    if args.category:
        category_path = create_named_path(path, args.category)
        if args.library:
            library.run_test(
                session=session,
                path=create_named_path(
                    category_path, args.operation_type,
                    subdirectory="libraries"),
                category=args.category,
                name=args.library,
                timeout=args.timeout
            )
            return

        if args.operation_type:
            operation_type.run_test(
                session=session,
                path=create_named_path(
                    category_path, args.operation_type,
                    subdirectory="operation_types"),
                category=args.category,
                name=args.operation_type,
                timeout=args.timeout
            )
            return

        category.run_tests(
            session=session,
            path=category_path,
            name=args.category,
            timeout=args.timeout
            )
        return

    if args.library or args.operation_type:
        logging.error(
            "To test a single operation type or library, you must enter a category")
        return

    if args.all:
        instance.run_tests(session=session, path=path, timeout=args.timeout)
        return

    logging.error(
        'You must choose either a category, library, or operation type to test. Or use -a or --all to test an entire directory'
        )


if __name__ == "__main__":
    main()
