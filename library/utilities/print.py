import os
import psutil
import json

from datetime import datetime, timedelta

def _get_row_info(pid, running_work, view_settings, as_raw_values=False):
    work = running_work[pid]
    phase_times = work.phase_times
    elapsed_time = (datetime.now() - work.datetime_start)
    elapsed_time = pretty_print_time(elapsed_time.seconds + elapsed_time.days * 86400)
    phase_time_log = []
    plot_id_prefix = ''
    if work.plot_id:
        plot_id_prefix = work.plot_id[0:7]
    for i in range(1, 5):
        if phase_times.get(i):
            phase_time_log.append(phase_times.get(i))

    row = [
        work.job.name if work.job else '?',
        work.k_size,
        plot_id_prefix,
        pid,
        work.datetime_start.strftime(view_settings['datetime_format']),
        elapsed_time,
        work.current_phase,
        ' / '.join(phase_time_log),
        work.progress,
        pretty_print_bytes(work.temp_file_size, 'gb', 0, " GiB"),
    ]
    if not as_raw_values:
        return [str(cell) for cell in row]
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


def get_job_data(jobs, running_work, view_settings, as_json=False):
    rows = []
    added_pids = []
    for job in jobs:
        for pid in job.running_work:
            if pid not in running_work:
                continue
            rows.append(_get_row_info(pid, running_work, view_settings, as_json))
            added_pids.append(pid)
    for pid in running_work.keys():
        if pid in added_pids:
            continue
        rows.append(_get_row_info(pid, running_work, view_settings, as_json))
        added_pids.append(pid)
    rows.sort(key=lambda x: (x[5]), reverse=True)
    for i in range(len(rows)):
        rows[i] = [str(i+1)] + rows[i]
    if as_json:
        jobs = dict(jobs=rows)
        print(json.dumps(jobs, separators=(',', ':')))
        return jobs
    return rows


def pretty_print_job_data(job_data):
    headers = ['num', 'job', 'k', 'plot_id', 'pid', 'start', 'elapsed_time', 'phase', 'phase_times', 'progress', 'temp_size']
    rows = [headers] + job_data
    return pretty_print_table(rows)

def print_json(jobs, running_work, view_settings):
    get_job_data(jobs=jobs, running_work=running_work, view_settings=view_settings, as_json=True)


def print_view(running_work):
    # Job Table
    job_data = get_job_data(jobs=jobs, running_work=running_work, view_settings=view_settings)
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(job_data)
