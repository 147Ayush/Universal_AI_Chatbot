# backend/verify_module_6.py
# Temporary check: confirms SSE streaming works, no frontend needed yet.

import httpx

with httpx.stream(
    "POST",
    "http://127.0.0.1:8000/chat/stream",
    json={"message": "Count from 1 to 5, one number per word.", "provider": "groq"},
    timeout=30,
) as response:
    print("Status:", response.status_code)
    for line in response.iter_lines():
        if line:
            print(line)