import requests
import concurrent.futures
import time
from datetime import datetime
import urllib3
import os
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_proxy_list(url):
    """Fetch the proxy list from the given URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
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
    except Exception as e:
        print(f"Error fetching proxy list: {e}")
        return []

def test_proxy(proxy, timeout=3):
    """Test a single HTTP proxy - FAST"""
    try:
        proxy_url = f"http://{proxy}"
        test_url = "https://www.google.com"

        start_time = time.perf_counter()

        response = requests.get(
            test_url,
            proxies={'http': proxy_url, 'https': proxy_url},
            timeout=timeout,
            verify=False,
            allow_redirects=True
        )

        response_time = time.perf_counter() - start_time

        if response.status_code == 200:
            if 'google' in response.text.lower():
                return proxy, True, response_time
            return proxy, True, response_time
        return proxy, False, 0

    except Exception:
        return proxy, False, 0

def draw_progress_bar(current, total, length=50, fast_count=0, speed=0.0):
    """Draw a progress bar"""
    progress = current / total
    filled = int(length * progress)
    bar = '█' * filled + '░' * (length - filled)
    percent = progress * 100

    speed_str = f"{speed:.1f}/s" if speed > 0 else ""

    sys.stdout.write(f'\r[{bar}] {percent:.1f}% | {current}/{total} | Fast: {fast_count} | {speed_str}')
    sys.stdout.flush()

def main():

    proxy_list_url = "https://github.com/databay-labs/free-proxy-list/raw/refs/heads/master/https.txt"
    output_file = "data/proxies.txt"

    print("=" * 70)
    print("🚀 ULTRA-FAST HTTP PROXY TESTER")
    print("=" * 70)
    print(f"📥 Source: {proxy_list_url}")
    print(f"🎯 Target: https://www.google.com")
    print(f"⚡ Only saving proxies with response time <= 3 seconds")
    print("=" * 70)

    os.makedirs("data", exist_ok=True)

    print("📥 Fetching proxy list...")
    proxies = fetch_proxy_list(proxy_list_url)

    if not proxies:
        print("❌ No proxies found!")
        return

    print(f"✅ Found {len(proxies)} HTTP proxies")
    print(f"🚀 Testing with 150 concurrent workers...")
    print("-" * 70)

    fast_proxies = []
    tested_count = 0
    fast_count = 0
    start_time = time.perf_counter()
    last_update = start_time
    last_count = 0

    print("\n🔥 Testing proxies:")
    draw_progress_bar(0, len(proxies), fast_count=0, speed=0.0)

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

    draw_progress_bar(len(proxies), len(proxies), fast_count, speed)
    sys.stdout.write('\n')

    elapsed_time = time.perf_counter() - start_time
    print("-" * 70)

    fast_proxies.sort(key=lambda x: x[1])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if fast_proxies:

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Fast HTTP Proxies (<=3s) - {timestamp}\n")
            f.write(f"# Tested: {len(proxies)} | Fast: {len(fast_proxies)}\n")
            f.write(f"# Success rate: {(len(fast_proxies)/len(proxies)*100):.1f}%\n\n")
            for proxy, speed in fast_proxies:
                f.write(f"{proxy}\n")

        print(f"✅ Saved {len(fast_proxies)} fast HTTP proxies to {output_file}")
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# No fast proxies found (<=3s) - {timestamp}\n")
        print("❌ No fast proxies found")

    print("\n" + "=" * 70)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 70)
    print(f"Total tested: {len(proxies)}")
    print(f"Fast proxies (<=3s): {len(fast_proxies)}")
    print(f"Success rate: {(len(fast_proxies)/len(proxies)*100):.1f}%")
    print(f"Total time: {elapsed_time:.2f}s")
    print(f"Average speed: {len(proxies)/elapsed_time:.1f} proxies/second")

    if fast_proxies:
        avg_speed = sum(speed for _, speed in fast_proxies) / len(fast_proxies)
        fastest = fast_proxies[0][1]
        slowest = fast_proxies[-1][1]

        print(f"\n⚡ Speed Statistics:")
        print(f"  Fastest: {fastest:.3f}s")
        print(f"  Slowest: {slowest:.3f}s")
        print(f"  Average: {avg_speed:.3f}s")

        print(f"\n🏆 Top 10 Fastest Proxies:")
        for i, (proxy, speed) in enumerate(fast_proxies[:10], 1):
            print(f"  {i:2}. {proxy.ljust(21)} - {speed:.3f}s")

        if len(fast_proxies) > 10:
            print(f"  ... and {len(fast_proxies) - 10} more")

    print("\n✅ DONE! Results saved to data/proxies.txt")

if __name__ == "__main__":
    print("🔧 Checking requirements...")
    try:
        import requests
    except ImportError:
        print("\n❌ ERROR: Install 'requests' first!")
        print("Command: pip install requests")
        input("Press Enter to exit...")
        sys.exit(1)

    main()
