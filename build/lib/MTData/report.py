from cliff.command import Command
import logging
import pandas as pd

def scaleReport(serverName):
    print(serverName)
    print('Scale Report!')

def clientReport(serverName):
    print(serverName)
    print('Client Report!')

class Report(Command):
    "A simple command that report basic static for missing data."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Report, self).get_parser(prog_name)
        subparser = parser.add_subparsers(help='sub-command help')

        # add a subcommand
        parser_a = subparser.add_parser('scale', help='scale help')
        parser_a.add_argument('serverName', nargs='?', default='.', type=str, help='serverName help')
        parser_a.set_defaults(func=scaleReport)


        # add another subcommand
        parser_b = subparser.add_parser('client', help='client help')
        parser_b.add_argument('serverName', nargs='?', default='.', type=str, help='serverName help')
        parser_b.set_defaults(func=clientReport)

        return parser

    def take_action(self, parsed_args):
        self.log.info('sending greeting')
        self.log.debug('debugging')
        parsed_args.func(parsed_args.serverName)
        self.app.stdout.write('AWS FILED \n')

class Error(Command):
    "Always raises an error"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('causing error')
        raise RuntimeError('this is the expected exception')
