import app from "../app.js";

const port = process.env.PORT || 8000;
const host = process.env.HOST || "0.0.0.0";
const server = app.listen(port, host, () => {
  console.log(
    `Server running on http://${
      host === "0.0.0.0" ? "localhost" : host
    }:${port}`
  );
});

// Debug instrumentation (can be removed later)
process.on("beforeExit", (code) => {
  console.log("[debug] beforeExit code=", code);
});
process.on("exit", (code) => {
  console.log("[debug] exit code=", code);
});
process.on("uncaughtException", (err) => {
  console.error("[debug] uncaughtException", err);
});
process.on("unhandledRejection", (reason) => {
  console.error("[debug] unhandledRejection", reason);
});

// Prevent accidental closure if nothing else is pending (should not be necessary but keeps process alive during diagnostics)
setInterval(() => {
  if (!server.listening) {
    console.warn("[debug] server no longer listening");
  }
}, 60000).unref();
