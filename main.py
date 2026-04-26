import argparse
import asyncio
import sys
import time
import aiohttp
import requests

async def fire_requests(session, url):
    try:
        async with session.get(url) as response:
            return response.status
    except Exception:
        return 0

async def start_load_test(url, concurrent_requests=500):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(0, concurrent_requests):
            try:
                coroutine = fire_requests(session, url)
                tasks.append(coroutine)
            except Exception as e:
                tasks.append(0)
                pass
                
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = round(end_time - start_time, 2)
        successes = results.count(200)
        
        print("\nRequest Report")
        print(f"Total Time: {total_time} seconds")
        print(f"Successful: {successes}/{concurrent_requests}")
        print(f"Failed: {concurrent_requests - successes}")


def main():
    parser = argparse.ArgumentParser(description="API Endpoint Load Tester")
    parser.add_argument('-c', '--count')
    parser.add_argument("endpoint", help="Api URL to stress test")

    args = parser.parse_args()
    url = args.endpoint
    
    concurrent_requests = 1000
    if (args.count and int(args.count) > 0 and int(args.count) < 1000000):
        concurrent_requests = int(args.count)

    try:
        response = requests.head(url, timeout=5)
        response.raise_for_status()
        print(f"Target is online: {response.status_code}")

    except requests.exceptions.HTTPError as e:
        print(f"Connection Error: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"{e}")
        sys.exit(1)

    asyncio.run(start_load_test(url, concurrent_requests))


if __name__ == "__main__":
    main()
