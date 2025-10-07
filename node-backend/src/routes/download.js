import express from 'express';
import { z } from 'zod';
import { apiKeyMiddleware } from '../middleware/apiKey.js';
import { fetchVideoInfo, mapInfoToResponse } from '../services/ytService.js';

const router = express.Router();

const downloadSchema = z.object({
  url: z.string().url('Invalid URL')
});

router.post('/download', apiKeyMiddleware, async (req, res) => {
  console.log('Download request received');
  const parse = downloadSchema.safeParse(req.body);
  if (!parse.success) {
    return res.status(400).json({ error: parse.error.issues.map(i => i.message).join(', ') });
  }

  const { url } = parse.data;

  // 🚫 Reject YouTube or TikTok URLs
  if (/youtube\.com|youtu\.be|tiktok\.com/i.test(url)) {
    return res.status(400).json({ error: 'Not Supported' });
  }

  try {
    const rawInfo = await fetchVideoInfo(url);
    const mapped = mapInfoToResponse(rawInfo);
    return res.json(mapped);
  } catch (err) {
    const message = typeof err?.stderr === 'string' ? err.stderr : (err.message || 'Unknown error');
    if (message.toLowerCase().includes('404')) {
      return res.status(400).json({
        title: null, uploader: null, upload_date: null, description: null,
        view_count: null, like_count: null, comment_count: null, duration: null,
        thumbnail: null, formats: [], error: message
      });
    }
    return res.status(500).json({
      title: null, uploader: null, upload_date: null, description: null,
      view_count: null, like_count: null, comment_count: null, duration: null,
      thumbnail: null, formats: [], error: 'Internal server error: ' + message
    });
  }
});

export default router;
