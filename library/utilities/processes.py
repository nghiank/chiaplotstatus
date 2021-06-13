import logging
import os
import platform
import psutil
import re
import subprocess


from copy import deepcopy
from datetime import datetime
from library.utilities.objects import Work

def is_windows():
    return platform.system() == 'Windows'


def get_chia_executable_name():
    return f'chia_plot'

def get_plot_directories(commands):
    try:
        temporary_index = commands.index('-t') + 1
        destination_index = commands.index('-d') + 1
    except ValueError:
        return None, None, None
    try:
        temporary2_index = commands.index('-2') + 1
    except ValueError:
        temporary2_index = None
    temporary_directory = commands[temporary_index]
    destination_directory = commands[destination_index]
    temporary2_directory = None
    if temporary2_index:
        temporary2_directory = commands[temporary2_index]
    return temporary_directory, temporary2_directory, destination_directory

def identify_drive(file_path, drives):
    if not file_path:
        return None
    for drive in drives:
        if drive not in file_path:
            continue
        return drive
    return None

def get_num_plot(commands):
    try:
        n_index = commands.index('-n') + 1
    except ValueError:
        return None
    return commands[n_index]

def get_plot_drives(commands):
    drives = get_system_drives()
    temporary_directory, temporary2_directory, destination_directory = get_plot_directories(commands=commands)
    temporary_drive = identify_drive(file_path=temporary_directory, drives=drives)
    destination_drive = identify_drive(file_path=destination_directory, drives=drives)
    temporary2_drive = None
    if temporary2_directory:
        temporary2_drive = identify_drive(file_path=temporary2_directory, drives=drives)
    return temporary_drive, temporary2_drive, destination_drive
def get_system_drives():
    drives = []
    for disk in psutil.disk_partitions(all=True):
        drive = disk.mountpoint
        if is_windows():
            drive = os.path.splitdrive(drive)[0]
        drives.append(drive)
    drives.sort(reverse=True)
    return drives

def cal_number_finished_plot(destination, datetime_start):
    return 0

def get_running_plots():
    chia_processes = []
    logging.info(f'Getting running chia-plotter')
    chia_executable_name = get_chia_executable_name()
    print("Chia chia_executable_name:" + chia_executable_name)
    for process in psutil.process_iter():
        try:
            if chia_executable_name not in process.name() and 'python' not in process.name().lower():
                continue
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
        try:
            if '-n' not in process.cmdline() or '-u' not in process.cmdline():
                continue
        except (psutil.ZombieProcess, psutil.NoSuchProcess):
            continue
        logging.info(f'Found chia plotting process: {process.pid}')
        datetime_start = datetime.fromtimestamp(process.create_time())
        chia_processes.append([datetime_start, process])
    chia_processes.sort(key=lambda x: (x[0]))
    running_work = {}
    for datetime_start, process in chia_processes:
        commands = []
        try:
            commands = process.cmdline()
        except (psutil.AccessDenied, RuntimeError):
            logging.info(f'Failed to find log file: {process.pid}')
        except psutil.NoSuchProcess:
            continue
        assumed_job = None
        logging.info(f'Finding associated job')
        temporary_directory, temporary2_directory, destination_directory = get_plot_directories(commands=commands)
        temporary_drive, temporary2_drive, destination_drive = get_plot_drives(commands=commands)
        num_plots = get_num_plot(commands=commands)
        work = deepcopy(Work())
        work.datetime_start = datetime_start
        work.finished_num_plots = cal_number_finished_plot(destination_directory, datetime_start)
        work.pid = process.pid        
        work.temporary_drive = temporary_drive
        work.temporary2_drive = temporary2_drive
        work.destination_drive = destination_drive
        work.max_num_plots = num_plots
        running_work[work.pid] = work
    return running_work