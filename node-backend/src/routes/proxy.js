import express from 'express';
import axios from 'axios';

const router = express.Router();

router.get('/proxy-video', async (req, res) => {
  const url = req.query.url;
  if (!url) return res.status(400).json({ detail: 'Missing url query parameter' });
  try {
    const response = await axios.get(url, { responseType: 'stream' });
    const contentType = response.headers['content-type'] || 'video/mp4';
    res.setHeader('Content-Type', contentType);
    res.setHeader('Access-Control-Allow-Origin', process.env.CORS_ORIGINS?.split(',')[0] || '*');
    response.data.pipe(res);
  } catch (err) {
    return res.status(400).json({ detail: 'Failed to fetch video stream' });
  }
});

export default router;
