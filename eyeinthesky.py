#!/usr/bin/env python3

import sys
import subprocess
import time
import os

def check_and_install_prerequisites():
    """Check if required modules and commands are installed, and prompt to install them if missing."""
    missing = []

    # Check for psutil
    try:
        import psutil
    except ImportError:
        missing.append("psutil")

    # Check for curses
    try:
        import curses
    except ImportError:
        if os.name == 'nt':  # On Windows, install windows-curses instead
            missing.append("windows-curses")
        else:
            missing.append("curses")

    # Check for sensors command (only on Linux)
    if os.name != 'nt':  # Skip sensors check on Windows
        try:
            subprocess.check_output(['sensors', '--version'], stderr=subprocess.STDOUT)
        except FileNotFoundError:
            missing.append("lm-sensors")

    # Check for wmi (only on Windows)
    if os.name == 'nt':
        try:
            import wmi
        except ImportError:
            missing.append("wmi")

    # If there are missing prerequisites, prompt the user to install them.
    if missing:
        print("The following prerequisites are missing:")
        for item in missing:
            print(f" - {item}")
        choice = input("Do you want to install them now? (y/n): ").strip().lower()
        if choice == 'y':
            for item in missing:
                if item == "psutil":
                    subprocess.run([sys.executable, "-m", "pip", "install", "psutil"])
                elif item == "windows-curses":
                    subprocess.run([sys.executable, "-m", "pip", "install", "windows-curses"])
                elif item == "curses":
                    print("Error: The 'curses' module cannot be installed via pip. It is typically included with Python on Unix-based systems.")
                    print("Please ensure your Python installation includes 'curses' and try again.")
                    sys.exit(1)
                elif item == "lm-sensors":
                    subprocess.run(["sudo", "apt-get", "install", "-y", "lm-sensors"])
                elif item == "wmi":
                    subprocess.run([sys.executable, "-m", "pip", "install", "wmi"])
            print("All prerequisites have been installed. Please re-run the script.")
            sys.exit(0)
        else:
            print("Exiting. Please install the missing prerequisites and try again.")
            sys.exit(1)

def get_temperatures():
    """Gets system temperatures."""
    if os.name == 'nt':  # Windows-specific temperature fetching
        try:
            import wmi
            w = wmi.WMI(namespace="root\\wmi")
            temperatures = {}
            for sensor in w.MSAcpi_ThermalZoneTemperature():
                temp_celsius = (sensor.CurrentTemperature / 10.0) - 273.15
                temperatures[sensor.InstanceName] = f"{temp_celsius:.1f} °C"
            return temperatures
        except wmi.x_wmi as e:
            if "OLE error 0x80041003" in str(e):
                return {"Temperature": "Permission denied. Run as administrator."}
            elif "OLE error 0x8004100c" in str(e):
                return {"Temperature": "Temperature data unavailable. Ensure your system supports thermal sensors."}
            else:
                return {"Temperature": f"Error: {e}"}
        except Exception as e:
            return {"Temperature": f"Error: {e}"}
    else:  # Linux-specific temperature fetching
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

def get_resource_usage():
    """Gets system resource usage."""
    import psutil
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
    import psutil
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    time.sleep(0.1)
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return processes[:10]

def main(stdscr):
    """Main function to display system information using curses."""
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)

    last_process_update = time.time()
    processes = []

    while True:
        stdscr.erase()
        height, width = stdscr.getmaxyx()

        stdscr.addstr(0, 0, "--- System Information ---")
        temperatures = get_temperatures()
        row = 1
        for key, value in temperatures.items():
            if row >= height - 1:
                break
            stdscr.addstr(row, 0, f"{key}: {value[:width - 1]}")
            row += 1

        if row < height - 1:
            stdscr.addstr(row, 0, "--- Resource Usage ---")
            row += 1
        resources = get_resource_usage()
        for key, value in resources.items():
            if row >= height - 1:
                break
            stdscr.addstr(row, 0, f"{key}: {value[:width - 1]}")
            row += 1

        current_time = time.time()
        if current_time - last_process_update >= 2:
            processes = get_running_processes()
            last_process_update = current_time

        if row < height - 1:
            stdscr.addstr(row, 0, "--- Top Running Processes ---")
            row += 1
        for proc in processes:
            if row >= height - 1:
                break
            process_info = (f"PID: {proc['pid']}, Name: {proc['name']}, "
                            f"CPU: {proc['cpu_percent']:.1f}%, Mem: {proc['memory_percent']:.1f}%")
            stdscr.addstr(row, 0, process_info[:width - 1])
            row += 1

        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('q'):
            break

if __name__ == "__main__":
    check_and_install_prerequisites()
    import curses
    curses.wrapper(main)