import assert from "node:assert/strict";
import { test } from "node:test";
import { detectPlatform } from "../public/assets/downloads.mjs";

test("desktop suggestions work with browser hints and legacy browsers", () => {
  for (const [device, expected] of [
    [{ userAgentData: { platform: "Windows" } }, "windows"],
    [{ userAgentData: { platform: "macOS" } }, "macos"],
    [{ userAgentData: { platform: "Linux" } }, "linux"],
    [{ platform: "Win32" }, "windows"],
    [{ platform: "MacIntel", maxTouchPoints: 0 }, "macos"],
    [{ platform: "Linux x86_64" }, "linux"],
    [{ userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" }, "windows"],
    [{ userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" }, "macos"],
    [{ userAgent: "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)" }, "linux"],
  ]) assert.equal(detectPlatform(device), expected, JSON.stringify(device));
});

test("phones and iPads never receive a desktop recommendation", () => {
  for (const device of [
    { userAgent: "Mozilla/5.0 (Linux; Android 14)" },
    { userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)" },
    { userAgent: "Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X)" },
    { platform: "MacIntel", maxTouchPoints: 5 },
    { userAgentData: { platform: "Android", mobile: false } },
    { userAgentData: { platform: "Windows", mobile: true } },
    { userAgent: "Windows Phone 10.0; Android 6.0" },
  ]) assert.equal(detectPlatform(device), "mobile", JSON.stringify(device));
});

test("unknown systems and ChromeOS keep the manual choices", () => {
  for (const device of [{}, { platform: "FreeBSD" }, { userAgent: "Mozilla/5.0 (X11; CrOS x86_64)", platform: "Linux x86_64" }]) {
    assert.equal(detectPlatform(device), null);
  }
});
