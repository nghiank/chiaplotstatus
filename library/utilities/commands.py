from library.parse.configuration import get_config_info
from library.utilities.processes import get_running_plots
from library.utilities.print import print_view
import time


def view_manager(loop=True):
	config = get_config_info()
	destination_directory = config['destination_directory']
	running_work = get_running_plots()
	print(running_work)
	while True:
		try:
			print_view(running_work=running_work)
			time.sleep(600)
		except KeyboardInterrupt:
			print("Stopped view.")
			exit()
		

