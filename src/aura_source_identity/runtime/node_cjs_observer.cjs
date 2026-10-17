/* Cooperative CommonJS source observer. Scope is limited to explicit specifier mappings. */
const fs = require("node:fs");
const crypto = require("node:crypto");
const Module = require("node:module");
const path = require("node:path");

const logPath = process.env.ASIG_RUNTIME_LOG;
const runId = process.env.ASIG_RUN_ID || null;
let expected = {};
try { expected = JSON.parse(process.env.ASIG_EXPECTED_SPECIFIERS || "{}"); } catch { expected = {}; }

function append(row) {
  if (!logPath) return;
  try { fs.appendFileSync(logPath, JSON.stringify({schema_version: 1, event: "module", runtime: "node-cjs", run_id: runId, pid: process.pid, ...row}) + "\n"); } catch {}
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
function sha(data) { return crypto.createHash("sha256").update(data).digest("hex"); }

const originalLoad = Module._load;
Module._load = function(request, parent, isMain) {
  if (Object.prototype.hasOwnProperty.call(expected, request)) {
    const expectedPath = path.resolve(String(expected[request]));
    try {
      const resolved = Module._resolveFilename(request, parent, isMain);
      const loadedPath = typeof resolved === "string" && path.isAbsolute(resolved) ? resolved : null;
      if (!loadedPath || !fs.existsSync(loadedPath) || !fs.statSync(loadedPath).isFile()) {
        append({specifier: request, expected_path: expectedPath, loaded_path: loadedPath, identity_status: "UNKNOWN", reason: "resolved module is not a readable filesystem file"});
      } else {
        const loadedHash = sha(readStable(loadedPath));
        const expectedHash = sha(readStable(expectedPath));
        const samePath = path.resolve(loadedPath) === expectedPath;
        const sameContent = loadedHash === expectedHash;
        append({
          specifier: request,
          expected_path: expectedPath,
          loaded_path: path.resolve(loadedPath),
          loaded_sha256: loadedHash,
          expected_sha256: expectedHash,
          path_match: samePath,
          content_match: sameContent,
          identity_status: samePath && sameContent ? "EXACT_MATCH" : sameContent ? "EQUIVALENT_COPY" : "MISMATCH"
        });
      }
    } catch (error) {
      append({specifier: request, expected_path: expectedPath, identity_status: "UNKNOWN", reason: String(error)});
    }
  }
  return originalLoad.apply(this, arguments);
};
