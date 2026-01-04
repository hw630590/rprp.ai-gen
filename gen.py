import requests
import concurrent.futures
import time
from datetime import datetime
import urllib3
import os
import sys
import subprocess

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_proxy_list(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        proxies = response.text.strip().split('\n')
        cleaned_proxies = []
        for proxy in proxies:
            proxy = proxy.strip()
            if proxy and ':' in proxy:
                parts = proxy.split(':')
                if len(parts) == 2 and parts[1].isdigit():
                    cleaned_proxies.append(proxy)
        return cleaned_proxies
    except:
        return []

def test_proxy(proxy, timeout=3):
    try:
        proxy_url = f"http://{proxy}"
        start_time = time.perf_counter()
        response = requests.get(
            "https://www.google.com",
            proxies={'http': proxy_url, 'https': proxy_url},
            timeout=timeout,
            verify=False
        )
        response_time = time.perf_counter() - start_time
        if response.status_code == 200:
            return proxy, True, response_time
        return proxy, False, 0
    except:
        return proxy, False, 0

def draw_progress_bar(current, total, fast_count=0, speed=0.0):
    length = 50
    progress = current / total
    filled = int(length * progress)
    bar = '█' * filled + '░' * (length - filled)
    percent = progress * 100
    speed_str = f"{speed:.1f}/s" if speed > 0 else ""
    sys.stdout.write(f'\r[{bar}] {percent:.1f}% | {current}/{total} | Fast: {fast_count} | {speed_str}')
    sys.stdout.flush()

def run_proxy_test():
    os.makedirs("data", exist_ok=True)
    
    print("=" * 70)
    print("🚀 HTTP PROXY TESTER")
    print("=" * 70)
    
    proxies = fetch_proxy_list("https://github.com/databay-labs/free-proxy-list/raw/refs/heads/master/https.txt")
    
    if not proxies:
        print("❌ No proxies found!")
        return []
    
    print(f"✅ Found {len(proxies)} HTTP proxies")
    print("🔥 Testing with 150 concurrent workers...")
    print("-" * 70)
    
    fast_proxies = []
    tested_count = 0
    fast_count = 0
    start_time = time.perf_counter()
    last_update = start_time
    last_count = 0
    
    print("\n🔥 Testing proxies:")
    draw_progress_bar(0, len(proxies))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy, 2): proxy for proxy in proxies}
        
        for future in concurrent.futures.as_completed(future_to_proxy):
            tested_count += 1
            proxy, is_working, response_time = future.result()
            
            if is_working and response_time <= 3.0:
                fast_count += 1
                fast_proxies.append((proxy, response_time))
            
            current_time = time.perf_counter()
            if current_time - last_update >= 0.5:
                speed = (tested_count - last_count) / (current_time - last_update)
                last_update = current_time
                last_count = tested_count
                draw_progress_bar(tested_count, len(proxies), fast_count, speed)
    
    draw_progress_bar(len(proxies), len(proxies), fast_count)
    sys.stdout.write('\n')
    
    fast_proxies.sort(key=lambda x: x[1])
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if fast_proxies:
        with open("data/proxies.txt", 'w', encoding='utf-8') as f:
            f.write(f"# Fast HTTP Proxies - {timestamp}\n")
            f.write(f"# Fast: {len(fast_proxies)}/{len(proxies)}\n\n")
            for proxy, speed in fast_proxies:
                f.write(f"{proxy}\n")
        print(f"✅ Saved {len(fast_proxies)} fast proxies")
    else:
        with open("data/proxies.txt", 'w', encoding='utf-8') as f:
            f.write(f"# No fast proxies found - {timestamp}\n")
        print("❌ No fast proxies found")
    
    return [proxy for proxy, _ in fast_proxies]

def main():
    print("🔧 Checking requirements...")
    try:
        import requests
    except:
        print("❌ Install: pip install requests")
        input("Press Enter to exit...")
        sys.exit(1)
    
    choice = input("\nFetch proxies & test them? (yes/no): ").strip().lower()
    
    proxies = []
    
    if choice in ['yes', 'y']:
        print("\n🔍 Running proxy test...")
        subprocess.run(["python", "proxy-test.py"], check=True)
        try:
            with open("data/proxies.txt", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxies.append(line)
        except:
            proxies = []
    else:
        try:
            with open("data/proxies.txt", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxies.append(line)
        except:
            print("❌ Could not read proxies.txt")
            return
    
    print(f"\n📋 Loaded {len(proxies)} proxies")
    
    import requests
    import time
    import random
    import string
    import threading
    from concurrent.futures import ThreadPoolExecutor
    
    os.makedirs("output", exist_ok=True)
    write_lock = threading.Lock()
    
    def setup_proxy(proxy_str):
        if not proxy_str:
            return None
        proxy_str = proxy_str.strip()
        if '@' in proxy_str:
            return {"http": f"http://{proxy_str}", "https": f"http://{proxy_str}"}
        elif proxy_str.count(':') == 3:
            host, port, user, password = proxy_str.split(':')
            return {"http": f"http://{user}:{password}@{host}:{port}", "https": f"http://{user}:{password}@{host}:{port}"}
        elif proxy_str.count(':') == 1:
            return {"http": f"http://{proxy_str}", "https": f"http://{proxy_str}"}
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
        payload = {"action": "signup", "data": {"confirmPassword": password, "email": email_address, "password": password, "verificationCode": verification_code}}
        try:
            response = session.post(url, headers=headers, json=payload, timeout=10)
            return response.json()
        except:
            return None
    
    def generate_password():
        uppercase = random.choice(string.ascii_uppercase)
        letters = ''.join(random.choices(string.ascii_lowercase, k=8))
        special = random.choice("!@#$%^&*()-_=+")
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
        while True:
            try:
                session = requests.Session()
                if proxy_str:
                    proxies = setup_proxy(proxy_str)
                    if proxies:
                        session.proxies = proxies
                
                inbox_data = create_temp_inbox_with_fallback(session)
                if not inbox_data:
                    time.sleep(5)
                    continue
                
                email_address = inbox_data.get('email')
                init_resp = send_initial_verification(session, email_address)
                if not init_resp:
                    time.sleep(3)
                    continue
                
                verification_code = None
                for attempt in range(1, 41):
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
                    time.sleep(5)
                
                if not verification_code:
                    time.sleep(3)
                    continue
                
                password = generate_password()
                final_resp = send_signup_verification(session, email_address, verification_code, password)
                if not final_resp:
                    time.sleep(3)
                    continue
                
                with write_lock:
                    with open("output/accs.txt", "a") as f:
                        f.write(f"{email_address}:{password}\n")
                    token = final_resp.get("accessToken", "")
                    if token:
                        with open("output/token.txt", "a") as f:
                            f.write(f"{token}\n")
                
                print(f"✅ Success! {email_address}")
                break
            except:
                time.sleep(5)
                continue
    
    import re
    
    try:
        total_runs = int(input("How many accounts: "))
        num_threads = int(input("Number of threads: "))
    except:
        print("Invalid input.")
        return
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for i in range(total_runs):
            proxy = proxies[i % len(proxies)] if proxies else None
            futures.append(executor.submit(worker, i, proxy))
        for future in futures:
            future.result()

if __name__ == '__main__':
    main()
