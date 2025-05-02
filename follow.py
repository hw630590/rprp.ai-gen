import asyncio
import aiohttp
import json

API_URL = "https://rprp.ai/api/user"

follow_id = input("https://rprp.ai/user/")

payload = {
    "action": "switchFollow",
    "data": {"followeeId": follow_id}
}

payload_str = json.dumps(payload)
payload_bytes = payload_str.encode('utf-8')
payload_length = len(payload_bytes)

def create_headers(token: str) -> dict:
    token = token.strip()

    cookie_str = (
        "i18n_redirected=en; G_ENABLED_IDPS=google; g_state={\"i_p\":1734046407079,\"i_l\":1}; "
        "user=%7B%22userInfo%22%3A%7B%22_id%22%3A%2268152ddda9be10eb9b143fe8%22%2C%22email%22%3A%22karoline27983%40disd.pigeonprotocol.com%22%2C%22name%22%3A%22User%231746218461707%22%2C%22bio%22%3A%22%22%2C%22picture%22%3A%22https%3A%2F%2Fcdn.rprp.ai%2Fdata%2Fimages%2Fpicture%2F66dbdbb248af2be8f8c14a78_1731564227284.png%22%2C%22isAdmin%22%3Afalse%2C%22isAffiliate%22%3Afalse%2C%22subscriptionPlan%22%3A%22free%22%2C%22creditPackages%22%3A…Lang%22%3A%22en%22%2C%22isLoadingChatList%22%3Afalse%2C%22isBackgroundEnabled%22%3Atrue%2C%22isFunctionsDisabled%22%3Afalse%2C%22isLoadingChatbotResponse%22%3Afalse%2C%22isLoadingChatHistory%22%3Afalse%2C%22userProfile%22%3A%7B%22userName%22%3A%22%22%2C%22userAvatar%22%3A%22%22%7D%2C%22modelRoute%22%3A%22rprp%22%7D; "
        "accessToken=eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..IC4bEedVJ5mootogWwojlQ.13Gr0hR3f6Pul20X7v7ogosjfbyT3fUde24xa70_PG6nSQDfqLj_vrSBWbPa3H3JmByKmKZ2CoYHVn4uBPTW1Q.nJHcY9WPr-PB1cvD8ES8ng"
    )
    
    return {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.5",
        "authorization": f"Bearer {token}",
        "Connection": "keep-alive",
        "Content-Length": str(payload_length),
        "content-type": "application/json",
        "Cookie": cookie_str,
        "DNT": "1",
        "Host": "rprp.ai",
        "Origin": "https://rprp.ai",
        "Priority": "u=0",
        "Referer": "https://rprp.ai/user/66dfb8fe6caf970c21849d65",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"
    }

async def send_request(session: aiohttp.ClientSession, token: str) -> None:
    headers = create_headers(token)
    try:
        async with session.post(API_URL, headers=headers, data=payload_bytes) as response:
            print("send follow")
    except Exception:
        print("send follow")

async def main():
    try:
        with open("output/token.txt", "r", encoding="latin1") as f:
            tokens = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading token file: {e}")
        return

    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, token) for token in tokens]
        await asyncio.gather(*tasks)

    print(f"send ({len(tokens)})")

if __name__ == "__main__":
    asyncio.run(main())
