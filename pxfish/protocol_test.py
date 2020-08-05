"""
code for running operation type tests
"""
import json
import logging


def parse_test_response(response):

    if response["result"] == "error":
        if response["error_type"] == "error":
            logging.error(response["message"])

        elif response["error_type"] == "assertion_failure":
            logging.info(
                    "Test failure: {}".format(
                        response["message"])
                    )

        elif response["error_type"] == "protocol_syntax_error":
            logging.info(
                    "Syntax error in protocol: {}".format(
                        response["message"])
                    )

        elif response["error_type"] == "protocol_error":
            logging.info(
                    "Execution error in protocol: {}".format(
                        response["message"])
                    )

        elif response["error_type"] == "test_syntax_error":
            logging.info(
                    "Syntax error in test: {}".format(
                        response["message"])
                    )

        elif response["error_type"] == "test_error":
            logging.info(
                    "Execution error in test: {} ".format(
                        response["message"])
                    )
        return
       # for entry in response.exception_backtrace:
       #     pass
    else:
        print("All tests passed")

    print(response.log)
    # response.backtrace
    time = None
    for entry in response["backtrace"]:
        if entry["operation"] == "display":
#            # previous value of time
            for show_object in entry["content"]:
                print(show_object)
#                # see showmatch in markdown converter
#                # "line" is object {"key": "value"}
#            time = entry["time"]
        elif entry["operation"] == "error":
            print("error") # see error.md

#
def format_table(content):
    formatted = ["<table>"]
    ary = json.loads(content)
    style = "border: 1px solid gray; text-align: center"
    for row in ary:
        newrow = ""
        for cell in row:
            this_style = style

            if isinstance(cell, dict):
                newcell = cell.get("content") or "?"
                if cell.get("class") == "td-filled-slot":
                    this_style = style + "; background-color: lightskyblue"

            else:
                newcell = cell

            newrow += "<td style=\"{}\">{}</td>".format(this_style, newcell)
        formatted.append("<tr>{}</tr>".format(newrow))

    formatted.append("</table>")
    
    return formatted
