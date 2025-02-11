import platform
import os

def get_os_info():
    os_name = platform.system()
    os_version = platform.version()
    
    if os_name == "Linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        os_version = line.split("=")[1].strip().strip('"')
                        break
        except FileNotFoundError:
            pass
    
    return os_name, os_version

def main():
    os_name, os_version = get_os_info()
    print(f"Operating System: {os_name}")
    print(f"OS Version: {os_version}")

if __name__ == "__main__":
    main()