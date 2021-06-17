from library.utilities.telegram import send
import platform
from datetime import datetime

def notify_num_jobs(job_data, config_info, last_notification):
	expect_num_plots = config_info['num_jobs']
	actual_num_plots = len(job_data)
	td = datetime.now() - last_notification['num_jobs']
	td_mins = int(round(td.total_seconds() / 60))
	if (td_mins >= config_info['notification_time_short']) and  (actual_num_plots < expect_num_plots):
		send("This machine '" + platform.node() + "' have number of jobs running " + str(actual_num_plots) + " less than expected " + str(expect_num_plots))
		last_notification['num_jobs'] = datetime.now()

def notify_warning_limit_hit(drive, usage, total, config_info, last_notification):    	
	if 'ramdisk' in drive:
		return		
	td = datetime.now() - last_notification['plot_nearly_full']
	td_mins = int(round(td.total_seconds() / 60))
	percent = usage/total
	if (percent > 0.9) and (td_mins > config_info['notification_time_long']):
		txt = "Destination folder '{drive:s}' almost full {percent:0.2f}% on '{machine:s}'"
		send(txt.format(drive=drive, percent=percent, machine=platform.node()))
		last_notification['plot_nearly_full'] = datetime.now()

def notify_machine_temperature(current, high, critical, last_notification):
	td = datetime.now() - last_notification['temperature']
	td_mins = int(round(td.total_seconds() / 60))	
	if (td_mins > 1) and (current > high):
		txt = "The machine '{machine:s}' is getting hot with temperature current={current:0.2f}, high={high:0.2f}, critical={critical:0.2f}."
		send(txt.format(machine=platform.node(), current=current, high=high, critical=critical))	
		last_notification['temperature'] = datetime.now()





