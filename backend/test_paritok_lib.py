import asyncio
from paritok import ParitokEngine, ParitokConfig
from paritok.config import GpuServerConfig


async def test_process_request():
    key = "pk_live_MHxyQjvpksZ39-KjUtyA9GZfSEWHsWZb"
    gpu_cfg = GpuServerConfig(api_key=key, base_url="https://www.paritok.com/api")

    cfg = ParitokConfig(use_gpu_server=True, gpu_server=gpu_cfg)
    engine = ParitokEngine(config=cfg)

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Analyze the civic issue."},
        {"role": "user", "content": "Route pothole at GPS (12.9716, 77.5946)."}
    ]

    try:
        if asyncio.iscoroutinefunction(engine.process_request):
            res = await engine.process_request(messages)
        else:
            res = engine.process_request(messages)
        print("process_request SUCCESS!")
        print(f"Type of res: {type(res)}")
        print(f"Res content: {res}")
    except Exception as e:
        print(f"process_request exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_process_request())
