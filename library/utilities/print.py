import os
import psutil
import json

from datetime import datetime, timedelta

def _get_row_info(pid, running_work):
    work = running_work[pid]
    elapsed_time = (datetime.now() - work.datetime_start)
    elapsed_time = pretty_print_time(elapsed_time.seconds + elapsed_time.days * 86400)
    row = [        
        str(work.finished_num_plots),
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
    headers = ['num', 'plot_complete', 'max_plot', 'pid', 'start', 'elapsed_time']
    rows = [headers] + job_data
    return pretty_print_table(rows)

def print_view(running_work):
    # Job Table
    job_data = get_job_data(running_work=running_work)
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(pretty_print_job_data(job_data))
