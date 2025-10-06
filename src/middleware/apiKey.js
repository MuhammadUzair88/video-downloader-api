import dotenv from 'dotenv';
dotenv.config();

export function apiKeyMiddleware(req, res, next) {
  const headerKey = req.header('X-API-Key');
  if (!headerKey || headerKey !== process.env.API_KEY) {
    return res.status(401).json({ detail: 'Invalid API Key' });
  }
  return next();
}
