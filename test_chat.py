import requests

try:
    response = requests.post(
        "http://localhost:8000/chat",
        json={"message": "What’s a good way to find housing for a single mom?"}
    )

    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

except Exception as e:
    print("An error occurred:", e)
