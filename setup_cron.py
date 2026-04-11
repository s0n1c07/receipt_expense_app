# setup_task_scheduler.py
import subprocess
import sys
import os

# Path to Python executable
python_path = sys.executable

# Path to your runner script (calls download_csv_file)
script_path = os.path.abspath('karanrun.py')

# Create Task Scheduler command
command = (
    f'schtasks /Create /SC DAILY /TN "DailyCSVDownload" /TR '
    f'"{python_path} {script_path}" /ST 06:00'
)

# Run the command
try:
    subprocess.run(command, shell=True, check=True)
    print("Task Scheduler job created: runs daily at 6:00 AM")
except subprocess.CalledProcessError as e:
    print("Failed to create scheduled task:", e)
