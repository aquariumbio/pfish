"""
code for running operation type tests
"""
import logging


def parse_test_response(response):
    """
    Reports test results

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

    return

    # for entry in response.exception_backtrace:
    #     pass

