# Video Downloader API (Node.js Version)

Reimplementation of the existing FastAPI video downloader service using Node.js, Express, and `yt-dlp` via `yt-dlp-exec`.

## Features Parity
- POST /api/v1/download : Returns video metadata and available formats.
- GET /api/v1/proxy-video : Proxies/streams remote video content to bypass CORS.
- API key header auth via `X-API-Key`.
- CORS restricted to configured origins.

## Environment Variables
Create a `.env` file:
```
API_KEY=your_secret_key
PORT=8000
CORS_ORIGINS=http://localhost:5173
```

## Install
```
npm install
```

## Run Dev
```
npm run dev
```

## Example Request
```
curl -X POST http://localhost:8000/api/v1/download \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_secret_key" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

## Response Shape
```json
{
  "title": "...",
  "uploader": "...",
  "upload_date": "YYYYMMDD",
  "description": "...",
  "view_count": 123,
  "like_count": 10,
  "comment_count": 5,
  "duration": 213,
  "thumbnail": "https://...",
  "formats": [
    {"quality":"HD","url":"...","format_note":"...","resolution":"1280x720","filesize":12345678}
  ],
  "error": null
}
```

## Next Steps (Suggested)
- Add tests (Jest + supertest).
- Add rate limiting & logging enhancements.
- Dockerize application.
- Implement caching for metadata (Redis).
- Add pagination / playlist handling.

---
This file documents only the Node.js port; original FastAPI app remains untouched.
