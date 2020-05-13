import sys
import os
import pydent
import argparse

from cliff.app import App
from cliff.commandmanager import CommandManager

class PyFish(App):

    def __init__(self):
        super(PyFish, self).__init__(
                command_manager=CommandManager('')
                )

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def main(argv=sys.argv[1:]):
        myapp = PyFish()
        return myapp.run(argv)

    if __name__ == '__main__':
        sys.exit(main(sys.argv[1:]))

