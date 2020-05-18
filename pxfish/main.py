import sys
import os
import pydent
import argparse

from cliff.app import App
from cliff.commandmanager import CommandManager

class PfishApp(App):

    def __init__(self):
        super(PfishApp, self).__init__(
                description='phoenix fish app',
                version='0.1'
                command_manager=CommandManager(''),
                deferred_help=True,
                )

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def main(argv=sys.argv[1:]):
        myapp = Pfish()
        return myapp.run(argv)

    if __name__ == '__main__':
        sys.exit(main(sys.argv[1:]))

