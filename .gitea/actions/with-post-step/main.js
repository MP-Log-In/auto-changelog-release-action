const { spawn } = require("child_process");
const { appendFileSync } = require("fs");
const { EOL } = require("os");

function run(cmd) {
  const proc = spawn(cmd, { stdio: "inherit", shell: true });
  proc.on("exit", code => process.exitCode = code);
}

const key = process.env.INPUT_KEY.toUpperCase();
if (process.env[`STATE_${key}`] !== undefined) {
  // ---------- POST ----------
  run(process.env.INPUT_POST);
} else {
  // ---------- MAIN ----------
  appendFileSync(process.env.GITHUB_STATE, `${key}=true${EOL}`);
  run(process.env.INPUT_MAIN);
}
