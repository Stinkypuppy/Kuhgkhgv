import requests
import threading
import queue
import time

# Your API keys
api_keys = [
    "474cc5660bmsh4d51ac2dfbbc02ep10a334jsnd03b2c147e87",
    "c40a705da9msh08559576e39cfc2p184731jsnba8578ac1533",
    "4a1f448d88mshd27d730da8788c3p18a227jsna8c7626fd1ba",
    "45d3c0706emsh5b97b7e479c3c68p16cb87jsn933e0f65068f",
    "90df15c47cmsh438b4c690f68c86p1e3368jsn3d8570a17131",
    "2cd35c799cmsh4b6b8f0574f8b6cp1c3d96jsne85eb6d02ed3",
    "c794571361msha6b9de9562c31dfp1b88afjsn0db3dd2a97bf",
    "2ca8e5a4e0mshe2f9618af3f546dp10b4aejsn048a88ed843e",
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
