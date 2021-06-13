import argparse

from library.utilities.exceptions import InvalidArgumentException
from library.utilities.commands import view_manager
parser = argparse.ArgumentParser(description='This is the status view of chia-plotter')

help_description = '''
I dont have a help yet
'''

parser.add_argument(
    dest='action',
    type=str,
    help=help_description,
)


args = parser.parse_args()

if args.action == 'view':
    view_manager()
else:
	error_message = 'Invalid action provided. The valid options are "view", "cal"'
	raise InvalidArgumentException(error_message)

