from fastapi import Header, HTTPException

API_KEY = "your_secure_api_key_here"

def get_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key
