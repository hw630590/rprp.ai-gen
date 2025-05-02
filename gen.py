import requests
import time
import re
import random
import string
import threading
from concurrent.futures import ThreadPoolExecutor
import os

os.makedirs("output", exist_ok=True)

write_lock = threading.Lock()

def create_temp_inbox(session):
    url = 'https://api.tempmail.lol/v2/inbox/create'
    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Origin': 'https://tempmail.lol',
        'Referer': 'https://tempmail.lol/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0'
    }
    payload = {"captcha": None, "domain": None, "prefix": ""}
    try:
        response = session.post(url, headers=headers, json=payload, timeout=10)
        print("⚙️    [DEBUG] create_temp_inbox: HTTP", response.status_code)
        print("⚙️    [DEBUG] create_temp_inbox response:", response.text)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error in create_temp_inbox:", e)
        try:
            print("Response content:", response.text)
        except Exception:
            pass
        return None

def check_inbox(session, token):
    url = f'https://api.tempmail.lol/v2/inbox?token={token}'
    headers = {
        'Accept': '*/*',
        'DNT': '1',
        'Origin': 'https://tempmail.lol',
        'Referer': 'https://tempmail.lol/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0'
    }
    try:
        response = session.get(url, headers=headers, timeout=10)
        print("⚙️     [DEBUG] check_inbox: HTTP", response.status_code)
        print("⚙️     [DEBUG] check_inbox response:", response.text)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error in check_inbox:", e)
        try:
            print("Response content:", response.text)
        except Exception:
            pass
        return None

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
        print("⚙️      [DEBUG] send_initial_verification: HTTP", response.status_code)
        print("⚙️      [DEBUG] send_initial_verification response:", response.text)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error in send_initial_verification:", e)
        try:
            print("Response content:", response.text)
        except Exception:
            pass
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
        print("⚙️    [DEBUG] send_signup_verification: HTTP", response.status_code)
        print("⚙️    [DEBUG] send_signup_verification response:", response.text)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error in send_signup_verification:", e)
        try:
            print("Response content:", response.text)
        except Exception:
            pass
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
    match = re.search(r'<strong[^>]*>(\d+)</strong>', content)
    if match:
        return match.group(1)
    return None

def worker(task_id, proxy):
    session = requests.Session()
    if proxy:
        session.proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        print(f"⚙️   [DEBUG] Using proxy: {proxy}")
    temp_data = create_temp_inbox(session)
    if not temp_data:
        print("⚙️    [DEBUG] Failed to create temp inbox. Exiting worker.")
        return
    email_address = temp_data.get('address')
    token = temp_data.get('token')
    if not email_address or not token:
        print("⚙️    [DEBUG] Missing email or token in temp inbox response. Exiting worker.")
        return

    init_resp = send_initial_verification(session, email_address)
    if not init_resp:
        print("⚙️    [DEBUG] Initial verification request failed. Exiting worker.")
        return

    verification_code = None
    while not verification_code:
        inbox = check_inbox(session, token)
        if inbox and isinstance(inbox, dict):
            emails = inbox.get('emails', [])
            for message in emails:
                content = message.get('html') or message.get('body', '')
                code = extract_verification_code(content)
                if code:
                    verification_code = code
                    break
        if not verification_code:
            print("⚙️    [DEBUG] No verification code found yet. Waiting 5 seconds...")
            time.sleep(5)
    print("⚙️    [DEBUG] Verification code extracted:", verification_code)

    password = generate_password()
    
    final_resp = send_signup_verification(session, email_address, verification_code, password)
    if not final_resp:
        print("⚙️    [DEBUG] Final signup verification request failed. Exiting worker.")
        return

    access_token = final_resp.get("accessToken", "")
    with write_lock:
        try:
            with open("output/accs.txt", "a") as acc_file:
                acc_file.write(f"{email_address}:{password}\n")
            if access_token:
                with open("output/token.txt", "a") as token_file:
                    token_file.write(f"{access_token}\n")
        except Exception as e:
            print("Error writing to file:", e)
    thread_name = threading.current_thread().name
    print(f"✅     THREAD-{thread_name} generated {email_address}")


if __name__ == '__main__':
    try:
        total_runs = int(input("How many accounts: "))
        num_threads = int(input("Number off threads: "))
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
