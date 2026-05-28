import httpx

from app.storage import save_json



response = httpx.get(
    "https://remoteok.com/api",
    timeout=20,
    headers={"User-Agent": "JobApplicationAssistant/0.1"},
)
response.raise_for_status()

data = response.json()

print(type(data))
print(len(data))
print(data[0])
print(data[1].keys())
print(data[1])

save_json(data, file_to_save="data/remoteok_jobs_samples.json")