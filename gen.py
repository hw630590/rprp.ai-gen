import requests
import concurrent.futures
import time
import urllib3
import os
import sys
import re
import random
import string
import threading
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_proxy_list(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        proxies = []
        for line in response.text.strip().split('\n'):
            line = line.strip()
            if line and ':' in line:
                parts = line.split(':')
                if len(parts) >= 2 and parts[1].isdigit():
                    proxies.append(line)
        return proxies
    except:
        return []

def test_http_proxy(proxy, test_url="https://www.google.com", timeout=2):
    try:
        proxy_dict = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        start_time = time.perf_counter()
        response = requests.get(test_url, proxies=proxy_dict, timeout=timeout, verify=False)
        response_time = time.perf_counter() - start_time
        if response.status_code == 200:
            return proxy, 'http', response_time, True
    except:
        pass
    return proxy, 'http', 0, False

def test_socks5_proxy(proxy, test_url="https://www.google.com", timeout=2):
    try:
        proxy_dict = {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'}
        start_time = time.perf_counter()
        response = requests.get(test_url, proxies=proxy_dict, timeout=timeout, verify=False)
        response_time = time.perf_counter() - start_time
        if response.status_code == 200:
            return proxy, 'socks5', response_time, True
    except:
        pass
    return proxy, 'socks5', 0, False

def draw_progress_bar(current, total, working_count=0, speed=0.0):
    length = 50
    progress = current / total if total > 0 else 0
    filled = int(length * progress)
    bar = '█' * filled + '░' * (length - filled)
    percent = progress * 100
    speed_str = f"{speed:.1f}/s" if speed > 0 else ""
    sys.stdout.write(f'\r[{bar}] {percent:.1f}% | {current}/{total} | Working: {working_count} | {speed_str}')
    sys.stdout.flush()

def run_proxy_test_choice():
    os.makedirs("data", exist_ok=True)
    
    print("=" * 70)
    print("🚀 SUPER FAST PROXY TESTER (<5 sec)")
    print("=" * 70)
    print("1. Test HTTP proxies only")
    print("2. Test SOCKS5 proxies only")
    print("3. Test both HTTP & SOCKS5")
    print("4. Skip testing, use existing proxies.txt")
    choice = input("\nSelect: ").strip()
    
    if choice == "4":
        try:
            with open("data/proxies.txt", "r") as f:
                proxies = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            proxies.append((parts[0], parts[1]))
                print(f"✅ Loaded {len(proxies)} proxies from file")
                return proxies
        except:
            print("❌ No proxies.txt found")
            return []
    
    print("\n⚡ Starting SUPER FAST test (2s timeout, 500 workers)...")
    
    all_proxies = []
    
    if choice in ["1", "3"]:
        http_url = "https://github.com/databay-labs/free-proxy-list/raw/refs/heads/master/http.txt"
        http_proxies = fetch_proxy_list(http_url)
        for proxy in http_proxies:
            all_proxies.append(('http', proxy))
    
    if choice in ["2", "3"]:
        socks5_url = "https://github.com/databay-labs/free-proxy-list/raw/refs/heads/master/socks5.txt"
        socks5_proxies = fetch_proxy_list(socks5_url)
        for proxy in socks5_proxies:
            all_proxies.append(('socks5', proxy))
    
    if not all_proxies:
        print("❌ No proxies found!")
        return []
    
    print(f"📊 Testing {len(all_proxies)} proxies...")
    
    working_proxies = []
    tested_count = 0
    working_count = 0
    start_time = time.perf_counter()
    last_update = start_time
    last_count = 0
    
    draw_progress_bar(0, len(all_proxies))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
        future_to_proxy = {}
        for proxy_type, proxy in all_proxies:
            if proxy_type == 'http':
                future = executor.submit(test_http_proxy, proxy)
            else:
                future = executor.submit(test_socks5_proxy, proxy)
            future_to_proxy[future] = (proxy_type, proxy)
        
        for future in concurrent.futures.as_completed(future_to_proxy):
            tested_count += 1
            proxy_type, proxy = future_to_proxy[future]
            proxy_addr, ptype, response_time, is_working = future.result()
            
            if is_working:
                working_count += 1
                working_proxies.append((proxy_addr, ptype, response_time))
            
            current_time = time.perf_counter()
            if current_time - last_update >= 0.1:
                speed = (tested_count - last_count) / (current_time - last_update)
                last_update = current_time
                last_count = tested_count
                draw_progress_bar(tested_count, len(all_proxies), working_count, speed)
            
            if time.perf_counter() - start_time > 5:
                break
    
    draw_progress_bar(len(all_proxies), len(all_proxies), working_count)
    sys.stdout.write('\n\n')
    
    elapsed = time.perf_counter() - start_time
    print(f"⚡ Test completed in {elapsed:.1f}s")
    print(f"✅ Found {len(working_proxies)} working proxies")
    
    if working_proxies:
        with open("data/proxies.txt", 'w', encoding='utf-8') as f:
            for proxy, ptype, speed in working_proxies:
                f.write(f"{ptype}:{proxy}\n")
    else:
        with open("data/proxies.txt", 'w', encoding='utf-8') as f:
            f.write("")
    
    return [(proxy, ptype) for proxy, ptype, _ in working_proxies]

def setup_proxy(proxy_str):
    if not proxy_str:
        return None
    
    if ':' not in proxy_str:
        return None
    
    parts = proxy_str.split(':', 1)
    
    if parts[0] in ['http', 'socks5']:
        protocol = parts[0]
        proxy_addr = parts[1]
    else:
        protocol = 'http'
        proxy_addr = proxy_str
    
    if '@' in proxy_addr:
        if protocol == 'http':
            return {"http": f"http://{proxy_addr}", "https": f"http://{proxy_addr}"}
        elif protocol == 'socks5':
            return {"http": f"socks5://{proxy_addr}", "https": f"socks5://{proxy_addr}"}
    
    proxy_parts = proxy_addr.split(':')
    
    if len(proxy_parts) == 4:
        host, port, user, password = proxy_parts
        if protocol == 'http':
            return {"http": f"http://{user}:{password}@{host}:{port}", "https": f"http://{user}:{password}@{host}:{port}"}
        elif protocol == 'socks5':
            return {"http": f"socks5://{user}:{password}@{host}:{port}", "https": f"socks5://{user}:{password}@{host}:{port}"}
    elif len(proxy_parts) == 2:
        if protocol == 'http':
            return {"http": f"http://{proxy_addr}", "https": f"http://{proxy_addr}"}
        elif protocol == 'socks5':
            return {"http": f"socks5://{proxy_addr}", "https": f"socks5://{proxy_addr}"}
    
    return None

def create_temp_inbox_tempmail_lol(session):
    try:
        url = 'https://api.tempmail.lol/v2/inbox/create'
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {"captcha": None, "domain": None, "prefix": ""}
        response = session.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 403:
            return None
        data = response.json()
        return {'email': data.get('address'), 'token': data.get('token'), 'service': 'tempmail.lol'}
    except:
        return None

def check_inbox_tempmail_lol(session, token):
    try:
        url = f'https://api.tempmail.lol/v2/inbox?token={token}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = session.get(url, headers=headers, timeout=10)
        return response.json()
    except:
        return None

def create_temp_inbox_temp_mail_io(session):
    try:
        url = 'https://api.internal.temp-mail.io/api/v3/email/new'
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {"min_name_length": 10, "max_name_length": 10}
        response = session.post(url, headers=headers, json=payload, timeout=15)
        data = response.json()
        return {'email': data.get('email'), 'token': data.get('token'), 'service': 'temp-mail.io'}
    except:
        return None

def check_inbox_temp_mail_io(session, email):
    try:
        url = f'https://api.internal.temp-mail.io/api/v3/email/{email}/messages'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = session.get(url, headers=headers, timeout=10)
        return response.json()
    except:
        return None

def create_temp_inbox_inboxes_com(session):
    try:
        url = 'https://inboxes.com/api/v2/inbox'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = session.post(url, headers=headers, json={}, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        email = data.get('email') or data.get('address')
        if not email:
            return None
        return {'email': email, 'token': data.get('token'), 'service': 'inboxes.com'}
    except:
        return None

def check_inbox_inboxes_com(session, email):
    try:
        email_clean = email.split('@')[0]
        url = f'https://inboxes.com/api/v2/inbox/{email_clean}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = session.get(url, headers=headers, timeout=10)
        return response.json()
    except:
        return {'msgs': []}

def send_initial_verification(session, email_address):
    url = "https://rprp.ai/api/auth/email"
    headers = {'User-Agent': 'Mozilla/5.0', 'content-type': 'application/json'}
    payload = {"action": "sendVerificationCode", "data": {"email": email_address, "type": "signup"}}
    try:
        response = session.post(url, headers=headers, json=payload, timeout=10)
        return response.json()
    except:
        return None

def send_signup_verification(session, email_address, verification_code, password):
    url = "https://rprp.ai/api/auth/email"
    headers = {'User-Agent': 'Mozilla/5.0', 'content-type': 'application/json'}
    payload = {
        "action": "signup",
        "data": {
            "confirmPassword": password,
            "email": email_address,
            "password": password,
            "verificationCode": verification_code,
            "userSource": {
                "initialCurrentUrl": "https://rprp.ai/?utm_source=powerusers&utm_medium=library&utm_campaign=powerusers",
                "referringDomain": "https://powerusers.ai/"
            }
        }
    }
    try:
        response = session.post(url, headers=headers, json=payload, timeout=10)
        # print(f"🔧 DEBUG - Signup response: {response.text}")
        # unprint the top line if it doesnt work properly
        return response.json()
    except:
        return None

def generate_password():
    uppercase = random.choice(string.ascii_uppercase)
    letters = ''.join(random.choices(string.ascii_lowercase, k=8))
    special = random.choice("!£$%^&*_-+=")
    password_list = list(uppercase + letters + special)
    random.shuffle(password_list)
    return ''.join(password_list)

def extract_verification_code(content):
    patterns = [r'\n\s*(\d{6})\s*\n', r'verification code[:\s]*(\d{6})', r'code[:\s]*(\d{6})', r'<strong[^>]*>(\d+)</strong>', r'\b(\d{6})\b']
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) == 6 and line.isdigit():
            return line
    return None

def create_temp_inbox_with_fallback(session):
    services = [("tempmail.lol", create_temp_inbox_tempmail_lol), ("temp-mail.io", create_temp_inbox_temp_mail_io), ("inboxes.com", create_temp_inbox_inboxes_com)]
    for service_name, create_func in services:
        result = create_func(session)
        if result and result.get('email'):
            return result
    return None

def check_temp_inbox(session, inbox_data):
    service = inbox_data.get('service')
    if service == 'tempmail.lol':
        return check_inbox_tempmail_lol(session, inbox_data.get('token'))
    elif service == 'temp-mail.io':
        return check_inbox_temp_mail_io(session, inbox_data.get('email'))
    elif service == 'inboxes.com':
        return check_inbox_inboxes_com(session, inbox_data.get('email'))
    return None

def worker(task_id, proxy_str):
    for attempt in range(3):
        try:
            session = requests.Session()
            if proxy_str:
                proxies = setup_proxy(proxy_str)
                if proxies:
                    session.proxies = proxies
            
            inbox_data = create_temp_inbox_with_fallback(session)
            if not inbox_data:
                continue
            
            email_address = inbox_data.get('email')
            init_resp = send_initial_verification(session, email_address)
            if not init_resp:
                continue
            
            verification_code = None
            for check_attempt in range(10):
                inbox = check_temp_inbox(session, inbox_data)
                if inbox:
                    service = inbox_data.get('service')
                    if service == 'tempmail.lol':
                        emails = inbox.get('emails', [])
                    elif service == 'temp-mail.io':
                        emails = inbox if isinstance(inbox, list) else []
                    elif service == 'inboxes.com':
                        emails = inbox.get('msgs', [])
                    else:
                        emails = []
                    
                    for msg in emails:
                        if service == 'tempmail.lol':
                            content = msg.get('html') or msg.get('body') or ''
                        elif service == 'temp-mail.io':
                            content = msg.get('body_text') or msg.get('body') or msg.get('html') or msg.get('text') or ''
                        elif service == 'inboxes.com':
                            content = msg.get('html') or msg.get('body') or msg.get('text') or ''
                        else:
                            content = ''
                        
                        if content:
                            code = extract_verification_code(str(content))
                            if code:
                                verification_code = code
                                break
                
                if verification_code:
                    break
                time.sleep(2)
            
            if not verification_code:
                continue
            
            password = generate_password()
            final_resp = send_signup_verification(session, email_address, verification_code, password)
            
            if not final_resp:
                continue
            
            with threading.Lock():
                with open("output/accs.txt", "a") as f:
                    f.write(f"{email_address}:{password}\n")
                
                token = final_resp.get("accessToken")
                if token:
                    with open("output/token.txt", "a") as f:
                        f.write(f"{token}\n")
            
            print(f"✅ {email_address}")
            return True
            
        except:
            continue
    
    return False

def main():
    print("🔧 Checking requirements...")
    try:
        import requests
    except:
        print("❌ Install: pip install requests")
        input("Press Enter to exit...")
        sys.exit(1)
    
    proxies = run_proxy_test_choice()
    
    if not proxies:
        print("❌ No proxies available!")
        return
    
    print(f"\n📋 Loaded {len(proxies)} proxies")
    
    os.makedirs("output", exist_ok=True)
    
    try:
        total_runs = int(input("How many accounts: "))
        num_threads = int(input("Number of threads: "))
    except:
        print("Invalid input.")
        return
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for i in range(total_runs):
            proxy = f"{proxies[i % len(proxies)][0]}:{proxies[i % len(proxies)][1]}" if proxies else None
            futures.append(executor.submit(worker, i, proxy))
        for future in futures:
            future.result()

if __name__ == '__main__':
    main()
