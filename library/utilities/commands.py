from library.parse.configuration import get_config_info
from library.utilities.processes import get_running_plots, identify_drive, get_system_drives
from library.utilities.print import print_view
import time

from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time


def view_manager(loop=True):
	running_work = get_running_plots()
	drives = {'temp': [], 'temp2': [], 'dest': []}
	print(running_work)
	system_drives = get_system_drives()
	for pid in running_work.keys():
		work = running_work[pid]
		directories = {
            'dest': work.destination_drive,
            'temp': work.temporary_drive,
            'temp2': work.temporary2_drive,
        }
		for key, directory_list in directories.items():
			if directory_list is None:
				continue
			if not isinstance(directory_list, list):
				directory_list = [directory_list]
			for directory in directory_list:
				drive = identify_drive(file_path=directory, drives=system_drives)
				if drive in drives[key]:
					continue
				drives[key].append(drive)
 
	print(drives)
	while True:
		try:
			print_view(running_work=running_work,drives=drives)
			time.sleep(600)
		except KeyboardInterrupt:
			print("Stopped view.")
			exit()
		

