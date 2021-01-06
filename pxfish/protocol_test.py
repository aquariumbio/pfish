"""
code for running operation type tests
"""
import json
import logging
import os


def log_backtrace(*, response, file_path):
    """"""
    file_path = os.path.join(file_path, 'test_results.json')

    with open(file_path, 'w') as file:
        file.write(json.dumps(response, indent=2))


def parse_test_response(response):
    """
    Reports test results
    Writes errors to screen

    Arguments:
        response (dict): response received after running test
    """
    if response["result"] == "error":
        if response["error_type"] == "error":
            logging.error(response["message"])

        elif response["error_type"] == "assertion_failure":
            logging.info(
                "Assertion error: %s", response["message"])

        elif response["error_type"] == "protocol_syntax_error":
            logging.info(
                'Syntax error in protocol: %s', response["message"])

        elif response["error_type"] == "protocol_error":
            logging.info(
                'Execution error in protocol: %s', response["message"])

        elif response["error_type"] == "test_syntax_error":
            logging.info(
                'Syntax error in test: %s', response["message"])

        elif response["error_type"] == "test_error":
            logging.info(
                'Execution error in test: %s', response["message"])

    else:
        logging.info(
            "All tests passed")

