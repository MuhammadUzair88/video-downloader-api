import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import morgan from "morgan";

import downloadRoute from "./routes/download.js";
import proxyRoute from "./routes/proxy.js";

dotenv.config();

export const app = express();

const allowedOrigins = (process.env.CORS_ORIGINS || "")
  .split(",")
  .map((o) => o.trim())
  .filter(Boolean);
app.use(
  cors({
    origin: (origin, cb) => {
      if (!origin) return cb(null, true);
      if (allowedOrigins.length === 0 || allowedOrigins.includes(origin))
        return cb(null, true);
      return cb(new Error("Not allowed by CORS"));
    },
    credentials: true,
    methods: ["GET", "POST"],
    allowedHeaders: ["Content-Type", "X-API-Key"],
  })
);

app.use(express.json({ limit: "1mb" }));
app.use(morgan("dev"));

app.get("/health", (_, res) => res.json({ status: "ok" }));

app.get('/', (req, res) => {
  res.send('🎉 Video Downloader API is running!');
});

app.use("/api/v1", downloadRoute);
app.use("/api/v1", proxyRoute);

// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: "Internal server error" });
});

export default app;
