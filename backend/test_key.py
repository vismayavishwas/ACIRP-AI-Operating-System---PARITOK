import asyncio
import httpx

async def main():
    urls = [
        "https://api.paritok.com/v1/chat/completions",
        "https://paritok.com/v1/chat/completions",
        "http://127.0.0.1:8080/v1/chat/completions",
        "https://api.paritok.ai/v1/chat/completions"
    ]
    headers = {
        "Authorization": "Bearer pk_live_MHxyQjvpksZ39-KjUtyA9GZfSEWHsWZb",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "paritok-4b-v1",
        "messages": [
            {"role": "user", "content": "Hello Paritok"}
        ]
    }
    for url in urls:
        print(f"Testing URL: {url}")
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                print(f"  -> SUCCESS! Status Code: {resp.status_code}")
                print(f"  -> Response: {resp.text[:150]}")
        except Exception as e:
            print(f"  -> Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
