import request from "supertest";
import { app } from "../app.js";
import assert from "assert";

// Set required env for test run
process.env.API_KEY = process.env.API_KEY || "testkey";

async function run() {
  try {
    // Health
    const health = await request(app).get("/health");
    assert.equal(health.status, 200, "Health endpoint failed");
    assert.deepEqual(health.body, { status: "ok" }, "Unexpected health body");

    // Unauthorized download
    const unauth = await request(app)
      .post("/api/v1/download")
      .send({ url: "https://example.com" });
    assert.equal(unauth.status, 401, "Expected 401 without API key");

    // Bad URL with auth
    const bad = await request(app)
      .post("/api/v1/download")
      .set("X-API-Key", process.env.API_KEY)
      .send({ url: "not-a-url" });
    assert.equal(bad.status, 400, "Expected 400 for invalid URL");

    console.log("SMOKE TEST PASSED");
    process.exit(0);
  } catch (err) {
    console.error("SMOKE TEST FAILED", err);
    process.exit(1);
  }
}

run();
