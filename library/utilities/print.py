from __future__ import print_function
import os
import psutil
import json
import pprint


from datetime import datetime, timedelta
from library.utilities.notify import notify_num_jobs, notify_warning_limit_hit, notify_machine_temperature
import socket

def _get_row_info(pid, running_work):
    work = running_work[pid]
    elapsed_time = (datetime.now() - work.datetime_start)
    elapsed_time = pretty_print_time(elapsed_time.seconds + elapsed_time.days * 86400)
    row = [        
        str(work.today_plots),
        str(work.yesterday_plots),
        str(work.total_plots),
        str(work.max_num_plots),   
        str(pid),
        work.datetime_start.strftime("%m/%d/%Y, %H:%M:%S"),
        elapsed_time,        
    ]
    return row


def pretty_print_bytes(size, size_type, significant_digits=2, suffix=''):
    if size_type.lower() == 'gb':
        power = 3
    elif size_type.lower() == 'tb':
        power = 4
    else:
        raise Exception('Failed to identify size_type.')
    calculated_value = round(size / (1024 ** power), significant_digits)
    calculated_value = f'{calculated_value:.{significant_digits}f}'
    return f"{calculated_value}{suffix}"


def pretty_print_time(seconds, include_seconds=True):
    total_minutes, second = divmod(seconds, 60)
    hour, minute = divmod(total_minutes, 60)
    return f"{hour:02}:{minute:02}{f':{second:02}' if include_seconds else ''}"


def pretty_print_table(rows):
    max_characters = [0 for cell in rows[0]]
    for row in rows:
        for i, cell in enumerate(row):
            length = len(cell)
            if len(cell) <= max_characters[i]:
                continue
            max_characters[i] = length

    headers = "   ".join([cell.center(max_characters[i]) for i, cell in enumerate(rows[0])])
    separator = '=' * (sum(max_characters) + 3 * len(max_characters))
    console = [separator, headers, separator]
    for row in rows[1:]:
        console.append("   ".join([cell.ljust(max_characters[i]) for i, cell in enumerate(row)]))
    console.append(separator)
    return "\n".join(console)

def get_job_data(running_work):
    rows = []
    added_pids = []
    for pid in running_work.keys():
        if pid in added_pids:
            continue
        rows.append(_get_row_info(pid, running_work))
        added_pids.append(pid)
    rows.sort(key=lambda x: (x[0]), reverse=True)
    for i in range(len(rows)):
        rows[i] = [str(i+1)] + rows[i]    
    return rows

def pretty_print_job_data(job_data):
    headers = ['num', 'yesterday', 'today', 'total plots', 'max_plots', 'pid', 'start', 'elapsed_time']     
    rows = [headers] + job_data
    return pretty_print_table(rows)


def get_drive_data(drives, config_info, last_notification):
    headers = ['type', 'drive', 'used', 'total', '%']
    rows = []
    drive_types = {}
    has_temp2 = False
    for drive_type, all_drives in drives.items():
        for drive in all_drives:
            if drive in drive_types:
                drive_type_list = drive_types[drive]
            else:
                drive_type_list = ['-', '-', '-']
            if drive_type == 'temp':
                drive_type_list[0] = 't'
            elif drive_type == 'temp2':
                has_temp2 = True
                drive_type_list[1] = '2'
            elif drive_type == 'dest':
                drive_type_list[2] = 'd'
            else:
                raise Exception(f'Invalid drive type: {drive_type}')
            drive_types[drive] = drive_type_list

    checked_drives = []
    for all_drives in drives.values():
        for drive in all_drives:
            if drive in checked_drives:
                continue
            checked_drives.append(drive)
            try:
                usage = psutil.disk_usage(drive)
            except (FileNotFoundError, TypeError):
                continue

            drive_type = '/'.join(drive_types[drive])

            row = [
                drive_type,
                drive,
                f'{pretty_print_bytes(usage.used, "tb", 2, "TiB")}',
                f'{pretty_print_bytes(usage.total, "tb", 2, "TiB")}',
                f'{usage.percent}%',
            ]
            notify_warning_limit_hit(drive, usage.used, usage.total, config_info, last_notification)
            rows.append(row)            
    rows = [headers] + rows
    return pretty_print_table(rows)    

def secs2hours(secs):
    mm, ss = divmod(secs, 60)
    hh, mm = divmod(mm, 60)
    return "%d:%02d:%02d" % (hh, mm, ss)

def print_temperature(last_notification):
    print("=================================================================================================")
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
    else:
        temps = {}
    if hasattr(psutil, "sensors_fans"):
        fans = psutil.sensors_fans()
    else:
        fans = {}
    if hasattr(psutil, "sensors_battery"):
        battery = psutil.sensors_battery()
    else:
        battery = None

    if not any((temps, fans, battery)):
        print("can't read any temperature, fans or battery info")
        return

    names = set(list(temps.keys()) + list(fans.keys()))
    for name in names:
        print(name)
        # Temperatures.
        if name in temps:
            print("    Temperatures:")
            for entry in temps[name]:
                notify_machine_temperature(entry.current, entry.high, entry.critical, last_notification)
                print("        %-20s %s°C (high=%s°C, critical=%s°C)" % (
                    entry.label or name, entry.current, entry.high,
                    entry.critical))
        # Fans.
        if name in fans:
            print("    Fans:")
            for entry in fans[name]:
                print("        %-20s %s RPM" % (
                    entry.label or name, entry.current))

    # Battery.
    if battery:
        print("Battery:")
        print("    charge:     %s%%" % round(battery.percent, 2))
        if battery.power_plugged:
            print("    status:     %s" % (
                "charging" if battery.percent < 100 else "fully charged"))
            print("    plugged in: yes")
        else:
            print("    left:       %s" % secs2hours(battery.secsleft))
            print("    status:     %s" % "discharging")
            print("    plugged in: no")
    print("=================================================================================================")

def print_view(running_work, drives, config_info, last_notification):
    # Job Table
    job_data = get_job_data(running_work=running_work)
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')     
    notify_num_jobs(job_data, config_info, last_notification)
    print(pretty_print_job_data(job_data))
    print()
    print()
    print("Machine info")     
    print(get_drive_data(drives, config_info, last_notification))

    print(f'CPU Usage: {psutil.cpu_percent()}%')    
    ram_usage = psutil.virtual_memory()
    print(f'RAM Usage: {pretty_print_bytes(ram_usage.used, "gb")}/{pretty_print_bytes(ram_usage.total, "gb", 2, "GiB")}'
                  f'({ram_usage.percent}%)')
    print_temperature(last_notification)

