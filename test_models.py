import urllib.request
import json

key = None
with open(".env") as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY="):
            key = line.strip().split("=", 1)[1].strip('"\'')

if not key:
    print("No key found")
else:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            for m in data.get("models", []):
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    print(m["name"])
    except Exception as e:
        print("ERROR:", e)
