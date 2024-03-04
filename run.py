import requests
import threading
import queue
import time

# Your API keys
api_keys = [
    "474cc5660bmsh4d51ac2dfbbc02ep10a334jsnd03b2c147e87",
    # Add more API keys here
]

# Proxy settings
proxies = {
    "http": "http://customer-guinnessgshep:moonwolf@pr.oxylabs.io:7777/",
    "https": "https://customer-guinnessgshep:moonwolf@pr.oxylabs.io:7777/"
}

# Rate limit settings
requests_per_key = 300
rate_limit_per_second = 10

# Thread worker function
def worker(q, lock):
    while not q.empty():
        api_key, url, querystring, headers = q.get()
        try:
            response = requests.get(url, headers=headers, params=querystring, proxies=proxies)
            data = response.json()
            with lock:
                # Write the required values to a file
                with open("device_info.txt", "a") as file:
                    file.write(f"{data['data']['device_id']}:{data['data']['install_id']}:{data['data']['device_info']['cdid']}:{data['data']['device_info']['openudid']}\n")
        except Exception as e:
            print(f"Request failed: {e}")
        finally:
            q.task_done()
            # Respect the rate limit
            time.sleep(1 / rate_limit_per_second)

# Prepare the queue
q = queue.Queue()
url = "https://tiktok-api15.p.rapidapi.com/index/Tiktok/RegisterDeviceInformation"
querystring = {"aid":"1233","os":"7.1.2","version":"250304"}

# Lock for file writing
lock = threading.Lock()

# Populate the queue with tasks
for api_key in api_keys:
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "tiktok-api15.p.rapidapi.com"
    }
    for _ in range(requests_per_key):
        q.put((api_key, url, querystring, headers))

# Start threads
threads = []
for _ in range(len(api_keys)):
    t = threading.Thread(target=worker, args=(q, lock))
    t.start()
    threads.append(t)

# Wait for all threads to complete
for t in threads:
    t.join()

print("All tasks completed.")
