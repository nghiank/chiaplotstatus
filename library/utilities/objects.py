class Work:
    work_id = None
    job = None
    pid = None
    plot_id = None
    

    temporary_drive = None
    temporary2_drive = None
    destination_drive = None

    current_phase = 1

    datetime_start = None
    datetime_end = None

    phase_times = {}
    total_run_time = None

    completed = False

    progress = 0
    temp_file_size = 0
    k_size = None