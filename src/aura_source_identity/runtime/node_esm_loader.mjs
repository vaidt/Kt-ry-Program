/* Cooperative Node ESM loader hook; records only explicitly mapped specifiers. */
import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";

const logPath = process.env.ASIG_RUNTIME_LOG;
const runId = process.env.ASIG_RUN_ID || null;
let expected = {};
try { expected = JSON.parse(process.env.ASIG_EXPECTED_SPECIFIERS || "{}"); } catch {}
const expectedByUrl = new Map();

function sha(data) { return crypto.createHash("sha256").update(data).digest("hex"); }
function append(row) {
  if (!logPath) return;
  try { fs.appendFileSync(logPath, JSON.stringify({schema_version: 1, event: "module", runtime: "node-esm", run_id: runId, pid: process.pid, ...row}) + "\n"); } catch {}
}
function readStable(file) {
  const before = fs.statSync(file);
  const data = fs.readFileSync(file);
  const after = fs.statSync(file);
  if (before.dev !== after.dev || before.ino !== after.ino || before.size !== after.size || before.mtimeMs !== after.mtimeMs || data.length !== after.size) {
    throw new Error("source changed while being observed");
  }
  return data;
}

export async function resolve(specifier, context, nextResolve) {
  const resolved = await nextResolve(specifier, context);
  if (Object.prototype.hasOwnProperty.call(expected, specifier)) {
    expectedByUrl.set(resolved.url, {specifier, expectedPath: path.resolve(String(expected[specifier]))});
  }
  return resolved;
}

export async function load(url, context, nextLoad) {
  const loaded = await nextLoad(url, context);
  const record = expectedByUrl.get(url);
  if (!record) return loaded;
  try {
    if (!url.startsWith("file:")) throw new Error("mapped ESM module did not resolve to a file URL");
    if (loaded.source == null) throw new Error("loader did not expose module source bytes");
    const loadedPath = fileURLToPath(url);
    const loadedSource = typeof loaded.source === "string" ? Buffer.from(loaded.source, "utf8") : Buffer.from(loaded.source);
    const stableSource = readStable(loadedPath);
    if (sha(stableSource) !== sha(loadedSource)) throw new Error("loader source differs from stable filesystem bytes");
    const expectedSource = readStable(record.expectedPath);
    const loadedHash = sha(loadedSource);
    const expectedHash = sha(expectedSource);
    const samePath = path.resolve(loadedPath) === record.expectedPath;
    const sameContent = loadedHash === expectedHash;
    append({
      specifier: record.specifier,
      expected_path: record.expectedPath,
      loaded_path: path.resolve(loadedPath),
      loaded_sha256: loadedHash,
      expected_sha256: expectedHash,
      path_match: samePath,
      content_match: sameContent,
      identity_status: samePath && sameContent ? "EXACT_MATCH" : sameContent ? "EQUIVALENT_COPY" : "MISMATCH"
    });
  } catch (error) {
    append({specifier: record.specifier, expected_path: record.expectedPath, loaded_path: url, identity_status: "UNKNOWN", reason: String(error)});
  }
  return loaded;
}
