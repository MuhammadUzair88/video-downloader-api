import youtubedl from "yt-dlp-exec";

/**
 * Fetch video info using yt-dlp without downloading.
 * @param {string} url
 * @returns {Promise<object>} raw info JSON
 */
export async function fetchVideoInfo(url) {
  // We request metadata only. Limit network time with a timeout.
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000); // 20s safety
    const result = await youtubedl(url, {
      dumpSingleJson: true,
      noWarnings: true,
      // Keep broad format to surface progressive options; yt-dlp still outputs full formats list.
      format: "bestvideo+bestaudio/best",
      // Pass signal for abort
      signal: controller.signal,
      cookies: process.env.INSTAGRAM_COOKIES,
    });
    clearTimeout(timeout);
    return result;
  } catch (e) {
    if (e.name === "AbortError") {
      throw new Error("Metadata fetch timed out");
    }
    throw e;
  }
}

/**
 * Map raw yt-dlp info to API response shape.
 */
export function mapInfoToResponse(info) {
  const rawFormats = Array.isArray(info.formats) ? info.formats : [];
  const enriched = rawFormats
    .filter((f) => f.vcodec !== "none" || f.acodec !== "none")
    .map((f) => {
      const hasVideo = f.vcodec !== "none";
      const hasAudio = f.acodec !== "none";
      return {
        quality: !hasVideo ? "Audio" : (f.height || 0) >= 720 ? "HD" : "SD",
        url: f.url,
        format_note: f.format_note || null,
        resolution:
          f.resolution ||
          (f.width && f.height ? `${f.width}x${f.height}` : null),
        filesize: typeof f.filesize === "number" ? f.filesize : null,
        hasVideo,
        hasAudio,
      };
    });

  // Progressive (both audio + video in one URL)
  const progressive = enriched.filter((f) => f.hasVideo && f.hasAudio);
  progressive.sort((a, b) => {
    const order = { HD: 3, SD: 2, Audio: 1 };
    return order[b.quality] - order[a.quality];
  });
  const representative = progressive[0] || enriched[0] || null;

  // Public formats list (omit internal flags)
  const publicFormats = enriched
    .map(({ hasVideo, hasAudio, ...rest }) => rest)
    .sort((a, b) => {
      const order = { HD: 3, SD: 2, Audio: 1 };
      return order[b.quality] - order[a.quality];
    });

  return {
    title: info.title || null,
    uploader: info.uploader || null,
    upload_date: info.upload_date || null,
    description: info.description || null,
    view_count: typeof info.view_count === "number" ? info.view_count : null,
    like_count: typeof info.like_count === "number" ? info.like_count : null,
    comment_count:
      typeof info.comment_count === "number" ? info.comment_count : null,
    duration: info.duration != null ? Math.trunc(info.duration) : null,
    thumbnail: info.thumbnail || null,
    formats: publicFormats,
    download_url: representative ? representative.url : null,
    error: null,
  };
}
