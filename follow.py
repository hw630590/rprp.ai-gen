import time
import json
import ssl
import urllib.request
import urllib.parse
import random

API_URL = "https://rprp.ai/api/user"

print("--- how to get user id ---")
print("1. log into your rprp.ai account or make one")
print("2. visit https://rprp.ai/profile/setting")
print("3. under where it says 'User#' you will find a 24-character string (e.g. i944t0c5e6e1co5pncfkgwp0)")
print("4. copy the user id and paste it below")
print("--------------------------")

follow_id = input("Enter user ID: ")

payload = {
    "action": "switchFollow",
    "data": {"followeeId": follow_id}
}

def create_request(token, target_id):
    token = token.strip()
    
    data = json.dumps(payload).encode('utf-8')
    
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "Host": "rprp.ai",
        "Origin": "https://rprp.ai",
        "Referer": f"https://rprp.ai/user/{target_id}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"
    }
    
    request = urllib.request.Request(API_URL, data=data, headers=headers, method='POST')
    return request

def send_follow(token, attempt=1):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        request = create_request(token, follow_id)
        
        with urllib.request.urlopen(request, context=context) as response:
            if response.status == 200:
                return True, "Success"
            else:
                return False, f"Status: {response.status}"
                
    except urllib.error.HTTPError as e:
        if e.code == 429:
            if attempt <= 3:
                wait_time = attempt * 5
                print(f"Rate limited, waiting {wait_time}s...", end=" ", flush=True)
                time.sleep(wait_time)
                return send_follow(token, attempt + 1)
            return False, "Rate limited (max retries)"
        elif e.code == 401:
            return False, "Invalid token"
        elif e.code == 403:
            return False, "CAPTCHA required"
        elif e.code == 404:
            return False, "User not found"
        elif e.code == 400:
            return False, "Bad request"
        elif e.code >= 500:
            if attempt <= 2:
                wait_time = attempt * 3
                print(f"Server error {e.code}, waiting {wait_time}s...", end=" ", flush=True)
                time.sleep(wait_time)
                return send_follow(token, attempt + 1)
            return False, f"Server error {e.code}"
        else:
            return False, f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection error"
    except Exception as e:
        return False, str(e)

def load_tokens():
    try:
        with open("output/token.txt", "r") as f:
            tokens = [line.strip() for line in f if line.strip()]
        return tokens
    except:
        return []

def main():
    print(f"\n{'='*50}")
    print("RPRP.AI Auto Follower")
    print(f"{'='*50}")
    
    if not follow_id:
        print("No user ID provided")
        return
    
    tokens = load_tokens()
    if not tokens:
        print("No tokens found in token.txt - try generating some accounts first")
        return
    
    print(f"\nTarget User: {follow_id}")
    print(f"Loaded Tokens: {len(tokens)}")
    print(f"\n{'─'*50}")
    
    success = 0
    total = len(tokens)
    
    for i, token in enumerate(tokens, 1):
        print(f"[{i}/{total}] Processing...", end=" ", flush=True)
        
        result, message = send_follow(token)
        
        if result:
            print(f"✓ Success")
            success += 1
        else:
            print(f"✗ {message}")
        
        if i < total:
            delay = random.uniform(0.3, 0.6)
            time.sleep(delay)
    
    print(f"\n{'─'*50}")
    print(f"Results: {success}/{total} successful")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
