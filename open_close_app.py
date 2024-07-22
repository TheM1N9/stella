import subprocess
import os
import winreg
import psutil


def get_installed_applications():
    """Search the registry and common directories for installed applications."""
    apps = {}

    # Common locations to search for installed applications
    common_paths = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\Windows\System32",
        r"C:\Users"
    ]

    for path in common_paths:
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".exe"):
                        app_name = file.replace(".exe", "").lower()
                        apps[app_name] = os.path.join(root, file)
        except Exception as e:
            print(f"Error accessing {path}: {e}")

    # Search the registry for installed applications
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for reg_path in reg_paths:
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
                subkey_name = winreg.EnumKey(reg_key, i)
                subkey = winreg.OpenKey(reg_key, subkey_name)
                try:
                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                    if display_name and install_location:
                        app_name = display_name.lower()
                        apps[app_name] = os.path.join(install_location, display_name + ".exe")
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error accessing registry path {reg_path}: {e}")

    return apps

# Cache for application paths
app_cache = get_installed_applications()

# Initialize speech recognition and text-to-speech engines
def open_application(app_name):
    """Open an application by name."""
    app_name = app_name.lower()
    system_apps = {
        'settings': 'start ms-settings:',
        'file explorer': 'start explorer',
        'control panel': 'control',
        'task manager': 'start taskmgr',
        'command prompt': 'cmd',
        'calculator': 'calc',
        'notepad': 'notepad',
        'paint': 'mspaint',
        'wordpad': 'write',
        'snipping tool': 'snippingtool',
        'character map': 'charmap',
        'disk cleanup': 'cleanmgr',
        'resource monitor': 'resmon',
        'windows media player': 'start wmplayer',
        'microsoft edge': 'start msedge',
        'vs code': 'code',
        'visual studio code': 'code'
    }

    if app_name in system_apps:
        try:
            subprocess.Popen(system_apps[app_name], shell=True)
            print(f"Opening {app_name}...")
            return f"Opening {app_name} successful."
        except Exception as e:
            print(f"Sorry, I couldn't open the application {app_name}. Error: {str(e)}")
            return f"Opening {app_name} failed."
        
    if app_name in app_cache:
        app_path = app_cache[app_name]
        try:
            if os.path.isfile(app_path):
                subprocess.Popen(app_path)
                print(f"Opening {app_name}...")
                return f"Opening {app_name} successful."
            else:
                print(f"Sorry, the application path for {app_name} is invalid.")
        except Exception as e:
            print(f"Sorry, I couldn't open the application {app_name}. Error: {str(e)}")
    else:
        print(f"Sorry, I couldn't find the application {app_name}.")

    return f"Opening {app_name} failed."


def close_application(app_name):
    """Close an application by name."""
    app_name = app_name.lower()
    closed = False
    system_apps = {
        'settings': 'ms-settings:',
        'file explorer': 'explorer.exe',
        'control panel': 'control.exe',
        'task manager': 'taskmgr.exe',
        'command prompt': 'cmd.exe',
        'calculator': 'calc.exe',
        'notepad': 'notepad.exe',
        'paint': 'mspaint.exe',
        'wordpad': 'write.exe',
        'snipping tool': 'snippingtool.exe',
        'character map': 'charmap.exe',
        'disk cleanup': 'cleanmgr.exe',
        'resource monitor': 'resmon.exe',
        'windows media player': 'wmplayer.exe',
        'microsoft edge': 'msedge.exe',
        'vs code': 'code.exe',
        'visual studio code': 'code.exe'
    }

    if app_name in system_apps:
        try:
            # Use taskkill to close the application forcefully
            subprocess.run(["taskkill", "/f", "/im", system_apps[app_name]], check=True)
            print(f"Closing {app_name}...")
            return f"Closing {app_name} successful."
        except subprocess.CalledProcessError as e:
            print(f"Sorry, I couldn't close the application {app_name}. Error: {str(e)}")
            return f"Closing {app_name} failed."
    for proc in psutil.process_iter(['pid', 'name']):
        if app_name in proc.info['name'].lower():
            try:
                proc.terminate()  # or proc.kill() if terminate() doesn't work
                closed = True
                print(f"Closing {app_name}...")
            except Exception as e:
                print(f"Sorry, I couldn't close the application {app_name}. Error: {str(e)}")
                return f"Closing {app_name} failed."

    if not closed:
        print(f"Sorry, I couldn't find the application {app_name} running.")
        return f"Closing {app_name} failed."

    return f"Closing {app_name} successful."
