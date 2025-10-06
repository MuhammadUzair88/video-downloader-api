import {
  fetchVideoInfo,
  mapInfoToResponse,
} from "../src/services/ytService.js";

const TEST_URL =
  process.argv[2] || "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

(async () => {
  try {
    console.log("Extracting (direct) metadata for", TEST_URL);
    const raw = await fetchVideoInfo(TEST_URL);
    const mapped = mapInfoToResponse(raw);
    console.log("Title:", mapped.title);
    console.log("Download URL:", mapped.download_url);
    console.log("Formats count:", mapped.formats.length);
    console.log("First 3 formats:", mapped.formats.slice(0, 3));
  } catch (e) {
    console.error("Direct extraction failed:", e.message || e);
    process.exit(1);
  }
})();
