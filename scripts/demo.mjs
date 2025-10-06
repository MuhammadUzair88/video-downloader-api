import fetch from "node-fetch";
import dotenv from "dotenv";

dotenv.config();

const API_KEY = process.env.API_KEY || "python_api_key_value";
const BASE = `http://localhost:${process.env.PORT || 8000}`;
const TEST_URL =
  process.argv[2] || "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

async function main() {
  console.log("Requesting metadata for", TEST_URL);
  const res = await fetch(`${BASE}/api/v1/download`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
    body: JSON.stringify({ url: TEST_URL }),
  });
  const json = await res.json();
  console.log("Status:", res.status);
  console.log("Title:", json.title);
  console.log("Download URL (progressive best):", json.download_url);
  console.log("First 3 formats:", json.formats?.slice(0, 3));
  if (json.error) {
    console.error("Error:", json.error);
    process.exit(1);
  }
  process.exit(0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
