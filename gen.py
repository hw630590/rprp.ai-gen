import requests
import time
import re
import random
import string
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import json

os.makedirs("output", exist_ok=True)

write_lock = threading.Lock()

def setup_proxy(proxy_str):
    """Setup proxy from any format"""
    if not proxy_str:
        return None

    proxy_str = proxy_str.strip()

    if proxy_str.startswith("brd.superproxy.io"):

        if proxy_str.count(':') >= 3:
            parts = proxy_str.split(':')
            if len(parts) >= 4:
                host = parts[0]
                port = parts[1]
                username = ':'.join(parts[2:-1])
                password = parts[-1]
                return {
                    "http": f"http://{username}:{password}@{host}:{port}",
                    "https": f"http://{username}:{password}@{host}:{port}"
                }

    if '@' in proxy_str:
        return {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}"
        }

    elif proxy_str.count(':') == 3:
        host, port, user, password = proxy_str.split(':')
        return {
            "http": f"http://{user}:{password}@{host}:{port}",
            "https": f"http://{user}:{password}@{host}:{port}"
        }

    elif proxy_str.count(':') == 1:
        return {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}"
        }

    return None

def create_temp_inbox_tempmail_lol(session):
    try:
        url = 'https://api.tempmail.lol/v2/inbox/create'
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Origin': 'https://tempmail.lol',
            'Referer': 'https://tempmail.lol/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        payload = {"captcha": None, "domain": None, "prefix": ""}
        response = session.post(url, headers=headers, json=payload, timeout=10)
        print(f"⚙️    [DEBUG] tempmail.lol create: HTTP {response.status_code}")

        if response.status_code == 403:
            print("⚠️  tempmail.lol: 403 Forbidden (rate limit)")
            return None

        response.raise_for_status()
        data = response.json()
        return {
            'email': data.get('address'),
            'token': data.get('token'),
            'service': 'tempmail.lol'
        }
    except Exception as e:
        print(f"Error in tempmail.lol create: {e}")
        return None

def check_inbox_tempmail_lol(session, token):
    try:
        url = f'https://api.tempmail.lol/v2/inbox?token={token}'
        headers = {
            'Accept': '*/*',
            'Origin': 'https://tempmail.lol',
            'Referer': 'https://tempmail.lol/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        response = session.get(url, headers=headers, timeout=10)
        print(f"⚙️     [DEBUG] tempmail.lol check: HTTP {response.status_code}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error in tempmail.lol check: {e}")
        return None

def create_temp_inbox_temp_mail_io(session):
    try:
        url = 'https://api.internal.temp-mail.io/api/v3/email/new'
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://temp-mail.org',
            'Referer': 'https://temp-mail.org/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        payload = {"min_name_length": 10, "max_name_length": 10}
        response = session.post(url, headers=headers, json=payload, timeout=15)
        print(f"⚙️    [DEBUG] temp-mail.io create: HTTP {response.status_code}")
        response.raise_for_status()
        data = response.json()
        return {
            'email': data.get('email'),
            'token': data.get('token'),
            'service': 'temp-mail.io'
        }
    except Exception as e:
        print(f"Error in temp-mail.io create: {e}")
        return None

def check_inbox_temp_mail_io(session, email):
    try:
        url = f'https://api.internal.temp-mail.io/api/v3/email/{email}/messages'
        headers = {
            'Accept': '*/*',
            'Origin': 'https://temp-mail.org',
            'Referer': 'https://temp-mail.org/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        response = session.get(url, headers=headers, timeout=10)
        print(f"⚙️     [DEBUG] temp-mail.io check: HTTP {response.status_code}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error in temp-mail.io check: {e}")
        return None

def create_temp_inbox_inboxes_com(session):
    try:
        url = 'https://inboxes.com/api/v2/inbox'
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Origin': 'https://inboxes.com',
            'Referer': 'https://inboxes.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        }
        response = session.post(url, headers=headers, json={}, timeout=10)
        print(f"⚙️    [DEBUG] inboxes.com create: HTTP {response.status_code}")

        if response.status_code != 200:
            print(f"⚠️  inboxes.com: HTTP {response.status_code}")
            return None

        data = response.json()
        email = data.get('email') or data.get('address')
        if not email:
            print(f"⚠️  inboxes.com: No email in response: {data}")
            return None

        return {
            'email': email,
            'token': data.get('token') or data.get('id'),
            'service': 'inboxes.com'
        }
    except Exception as e:
        print(f"Error in inboxes.com create: {e}")
        return None

def check_inbox_inboxes_com(session, email):
    try:

        email_clean = email.split('@')[0]
        url = f'https://inboxes.com/api/v2/inbox/{email_clean}'
        headers = {
            'Accept': '*/*',
            'Origin': 'https://inboxes.com',
            'Referer': 'https://inboxes.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        }
        response = session.get(url, headers=headers, timeout=10)
        print(f"⚙️     [DEBUG] inboxes.com check: HTTP {response.status_code}")

        if response.status_code == 404:
            print("⚠️  inboxes.com: 404 Not Found (maybe wrong endpoint)")
            return {'msgs': []}

        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error in inboxes.com check: {e}")
        return {'msgs': []}

def send_initial_verification(session, email_address):
    url = "https://rprp.ai/api/auth/email"
    headers = {
        'Accept': 'application/json',
        'content-type': 'application/json',
        'Cookie': 'i18n_redirected=en; G_ENABLED_IDPS=google; g_state={"i_p":1734046407079,"i_l":1}',
        'DNT': '1',
        'Origin': 'https://rprp.ai',
        'Referer': 'https://rprp.ai/auth/signup',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0'
    }
    payload = {
        "action": "sendVerificationCode",
        "data": {
            "confirmPassword": "",
            "email": email_address,
            "password": "",
            "type": "signup",
            "verificationCode": ""
        }
    }
    try:
        response = session.post(url, headers=headers, json=payload, timeout=10)
        print(f"⚙️      [DEBUG] send_initial_verification: HTTP {response.status_code}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error in send_initial_verification: {e}")
        return None

def send_signup_verification(session, email_address, verification_code, password):
    url = "https://rprp.ai/api/auth/email"
    headers = {
        'Accept': 'application/json',
        'content-type': 'application/json',
        'Cookie': 'i18n_redirected=en; G_ENABLED_IDPS=google; g_state={"i_p":1734046407079,"i_l":1}',
        'DNT': '1',
        'Origin': 'https://rprp.ai',
        'Referer': 'https://rprp.ai/auth/signup',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0'
    }
    payload = {
        "action": "signup",
        "data": {
            "confirmPassword": password,
            "email": email_address,
            "password": password,
            "userSource": {
                "initialCurrentUrl": "https://rprp.ai/?utm_source=powerusers&utm_medium=library&utm_campaign=powerusers",
                "referringDomain": "https://powerusers.ai/"
            },
            "verificationCode": verification_code
        }
    }
    try:
        response = session.post(url, headers=headers, json=payload, timeout=10)
        print(f"⚙️    [DEBUG] send_signup_verification: HTTP {response.status_code}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error in send_signup_verification: {e}")
        return None

def generate_password():
    uppercase = random.choice(string.ascii_uppercase)
    letters = ''.join(random.choices(string.ascii_lowercase, k=8))
    special = random.choice("!@#$%^&*()-_=+")
    password_list = list(uppercase + letters + special)
    random.shuffle(password_list)
    password = ''.join(password_list)
    print("⚙️     [DEBUG] Generated password:", password)
    return password

def extract_verification_code(content):

    content = str(content).strip()

    patterns = [

        r'\n\s*(\d{6})\s*\n',

        r'verification code[:\s]*(\d{6})',
        r'code[:\s]*(\d{6})',

        r'<strong[^>]*>(\d+)</strong>',

        r'\b(\d{6})\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            code = match.group(1)
            print(f"⚙️    [DEBUG] Found code with pattern '{pattern}': {code}")
            return code

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) == 6 and line.isdigit():
            print(f"⚙️    [DEBUG] Found 6-digit line: {line}")
            return line

    print(f"⚙️    [DEBUG] No code found in content (length: {len(content)})")
    if len(content) < 500:  

        print(f"⚙️    [DEBUG] Content was: {content}")

    return None

def create_temp_inbox_with_fallback(session):
    """Try services in order: tempmail.lol -> temp-mail.io -> inboxes.com"""
    services = [
        ("tempmail.lol", create_temp_inbox_tempmail_lol),
        ("temp-mail.io", create_temp_inbox_temp_mail_io),
        ("inboxes.com", create_temp_inbox_inboxes_com)
    ]

    for service_name, create_func in services:
        print(f"⚙️    [DEBUG] Trying {service_name}...")
        result = create_func(session)
        if result and result.get('email'):
            print(f"✅ Created email with {service_name}: {result['email']}")
            return result
        print(f"⚠️  {service_name} failed, trying next...")

    return None

def check_temp_inbox(session, inbox_data):
    """Check inbox based on service type"""
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
                    print(f"⚙️   [DEBUG] Using proxy: {proxy_str}")

            print(f"⚙️    [DEBUG] Creating temp email...")
            inbox_data = create_temp_inbox_with_fallback(session)

            if not inbox_data or not inbox_data.get('email'):
                print(f"❌ All temp email services failed")
                time.sleep(5)
                continue

            email_address = inbox_data.get('email')
            token = inbox_data.get('token')
            service = inbox_data.get('service')
            print(f"✅ Using email: {email_address} from {service}")

            print("⚙️    [DEBUG] Sending verification request...")
            init_resp = send_initial_verification(session, email_address)
            if not init_resp:
                print("❌ Initial verification request failed")
                time.sleep(3)
                continue

            verification_code = None
            for attempt in range(1, 41):  

                print(f"⚙️    [DEBUG] Checking inbox attempt {attempt}/40...")

                inbox = check_temp_inbox(session, inbox_data)

                if inbox:

                    if service == 'tempmail.lol':
                        emails = inbox.get('emails', [])
                        print(f"⚙️    [DEBUG] tempmail.lol has {len(emails)} messages")
                    elif service == 'temp-mail.io':
                        emails = inbox if isinstance(inbox, list) else []
                        print(f"⚙️    [DEBUG] temp-mail.io has {len(emails)} messages")
                    elif service == 'inboxes.com':
                        emails = inbox.get('msgs', [])
                        print(f"⚙️    [DEBUG] inboxes.com has {len(emails)} messages")
                    else:
                        emails = []

                    for i, msg in enumerate(emails):

                        if service == 'tempmail.lol':
                            content = msg.get('html') or msg.get('body') or ''
                        elif service == 'temp-mail.io':
                            content = msg.get('body_text') or msg.get('body') or msg.get('html') or msg.get('text') or ''
                        elif service == 'inboxes.com':
                            content = msg.get('html') or msg.get('body') or msg.get('text') or ''
                        else:
                            content = ''

                        if content:
                            print(f"⚙️    [DEBUG] Checking message {i+1}, length: {len(str(content))}")

                            if attempt > 1 and not verification_code and len(str(content)) < 1000:
                                print(f"⚙️    [DEBUG] Content preview: {str(content)[:200]}...")

                            code = extract_verification_code(str(content))
                            if code:
                                verification_code = code
                                print(f"✅ Found verification code: {verification_code}")
                                break

                if verification_code:
                    break

                print("⚙️    [DEBUG] No code found, waiting 5 seconds...")
                time.sleep(5)

            if not verification_code:
                print(f"❌ No verification code found after 40 attempts")
                time.sleep(3)
                continue

            password = generate_password()
            final_resp = send_signup_verification(session, email_address, verification_code, password)
            if not final_resp:
                print("❌ Signup failed")
                time.sleep(3)
                continue

            with write_lock:
                with open("output/accs.txt", "a") as f:
                    f.write(f"{email_address}:{password}\n")

                token = final_resp.get("accessToken", "")
                if token:
                    with open("output/token.txt", "a") as f:
                        f.write(f"{token}\n")

            print(f"✅ Success! Created {email_address} using {service}")
            break

        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)
            continue

if __name__ == '__main__':
    try:
        total_runs = int(input("How many accounts: "))
        num_threads = int(input("Number of threads: "))
    except ValueError:
        print("Invalid input. Please enter integer values.")
        exit(1)

    proxies = []
    try:
        with open("data/proxies.txt", "r") as f:
            for line in f:
                proxy = line.strip()
                if proxy:
                    proxies.append(proxy)
    except Exception as e:
        print("Error reading proxies file:", e)
        proxies = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for i in range(total_runs):
            proxy = proxies[i % len(proxies)] if proxies else None
            futures.append(executor.submit(worker, i, proxy))
        for future in futures:
            future.result()
