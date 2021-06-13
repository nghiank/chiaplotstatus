from library.parse.configuration import get_config_info
from library.utilities.processes import get_running_plots
from library.utilities.print import print_view, print_json


def view_manager(loop=True):
	config = get_config_info()
	destination_directory = config['destination_directory']
	works = get_running_plots()
	print(works)
	#print_view(running_work=works)
		

