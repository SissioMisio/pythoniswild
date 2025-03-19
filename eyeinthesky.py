#!/usr/bin/env python3

import sys
import subprocess
import time
import curses
import psutil  # Importing psutil for system monitoring.

def check_and_install_prerequisites():
    """Check if required modules and commands are installed, and prompt to install them if missing."""
    missing = []

    # Check for psutil
    try:
        import psutil
    except ImportError:
        missing.append("psutil")

    # Check for curses (typically included with Python on Unix-based systems). 
    try:
        import curses
    except ImportError:
        print("Error: The 'curses' module is not available. It is typically included with Python on Unix-based systems.")
        sys.exit(1)

    # Check for sensors command.
    try:
        subprocess.check_output(['sensors', '--version'], stderr=subprocess.STDOUT)
    except FileNotFoundError:
        missing.append("lm-sensors")

    # If there are missing prerequisites, prompt the user to install them. I ain't installing them.
    if missing:
        print("The following prerequisites are missing:")
        for item in missing:
            print(f" - {item}")
        choice = input("Do you want to install them now? (y/n): ").strip().lower()
        if choice == 'y':
            for item in missing:
                if item == "psutil":
                    subprocess.run([sys.executable, "-m", "pip", "install", "psutil"])
                elif item == "lm-sensors":
                    subprocess.run(["sudo", "apt-get", "install", "-y", "lm-sensors"])
            print("All prerequisites have been installed. Please re-run the script.")
            sys.exit(0)
        else:
            print("Exiting. Please install the missing prerequisites and try again.")
            sys.exit(1)

def get_temperatures():
    """Gets system temperatures using the sensors command."""
    temperatures = {}
    try:
        sensors_output = subprocess.check_output(['sensors']).decode('utf-8')
        for line in sensors_output.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if '°C' in value:
                    temperatures[key] = value
    except Exception as e:
        temperatures['sensors'] = f"Error: {e}"

    return temperatures

# Balls. Huh? Sorry, I was just thinking about how I'm going to die alone.
def get_resource_usage():
    """Gets system resource usage."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory_percent = psutil.virtual_memory().percent
    disk_io = psutil.disk_io_counters()
    net_io = psutil.net_io_counters()

    return {
        'CPU Usage': f'{cpu_percent}%',
        'Memory Usage': f'{memory_percent}%',
        'Disk Read': f'{disk_io.read_bytes / (1024 * 1024):.2f} MB',
        'Disk Write': f'{disk_io.write_bytes / (1024 * 1024):.2f} MB',
        'Network Sent': f'{net_io.bytes_sent / (1024 * 1024):.2f} MB',
        'Network Received': f'{net_io.bytes_recv / (1024 * 1024):.2f} MB',
    }

def get_running_processes():
    """Gets the top 10 processes sorted by CPU usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Skip processes that no longer exist or cannot be accessed
            continue

    # Allow psutil to calculate CPU usage over a short interval. SHOULD be enough.
    time.sleep(0.1)

    # Sort processes by CPU usage in descending order
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

    # Return the top 10 processes. Hopefully.
    return processes[:10]

def main(stdscr):
    """Main function to display system information using curses."""
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)  # Make getch() non-blocking
    stdscr.timeout(1000)  # Refresh every 1 second

    last_process_update = time.time()  # Track the last time processes were updated
    processes = []  # Initialize processes list

    while True:
        stdscr.clear()

        # Get terminal dimensions
        height, width = stdscr.getmaxyx()

        # Display system temperatures
        stdscr.addstr(0, 0, "--- System Information ---")
        temperatures = get_temperatures()
        row = 1
        for key, value in temperatures.items():
            if row >= height - 1:  # Prevent writing outside the terminal height
                break
            stdscr.addstr(row, 0, f"{key}: {value[:width - 1]}")  # Truncate text to fit width. I'm not going to bother with word wrapping.
            row += 1

        # Display resource usage
        if row < height - 1:
            stdscr.addstr(row, 0, "--- Resource Usage ---")
            row += 1
        resources = get_resource_usage()
        for key, value in resources.items():
            if row >= height - 1:  # Prevent writing outside the terminal height. Word wrapping is for losers. Raw dogging it. Literally.
                break
            stdscr.addstr(row, 0, f"{key}: {value[:width - 1]}")  # Truncate text to fit width. 
            row += 1

        # Update processes every 2 seconds or the console will flicker like a strobe light. Jeez I hate TN panels.
        current_time = time.time()
        if current_time - last_process_update >= 2:
            processes = get_running_processes()
            last_process_update = current_time

        # Display top running processes
        if row < height - 1:
            stdscr.addstr(row, 0, "--- Top Running Processes ---")
            row += 1
        for proc in processes:
            if row >= height - 1:  # Prevent writing outside the terminal height or the compiler will have a field day.
                break
            process_info = (f"PID: {proc['pid']}, Name: {proc['name']}, "
                            f"CPU: {proc['cpu_percent']:.1f}%, Mem: {proc['memory_percent']:.1f}%")
            stdscr.addstr(row, 0, process_info[:width - 1])  # Truncate text to fit width
            row += 1

        stdscr.refresh()

        # Exit on 'q' key press. To whoever changes this in the future, good luck. This is coded with sticks and bubblegum.
        key = stdscr.getch()
        if key == ord('q'):
            break

if __name__ == "__main__":
    check_and_install_prerequisites()
    curses.wrapper(main)