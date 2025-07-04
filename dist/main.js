const cp = require("child_process");
const path = require("path");
const fs = require("fs");

function run(script) {
  cp.execFileSync(script, { stdio: "inherit", shell: true });
}

function exportOutput(key, value) {
  fs.appendFileSync(process.env.GITHUB_OUTPUT, `${key}=${value}\n`);
}

function setEnv(key, value) {
  fs.appendFileSync(process.env.GITHUB_ENV, `${key}=${value}\n`);
}

function main() {
  const script = path.join(__dirname, "..", "scripts", "detect-version-change.sh");


  run(script);

  // Hier nehmen wir an, dass das Script selbst bereits `version_changed=true/false`
  // in $GITHUB_OUTPUT geschrieben hat.
  // Zur Sicherheit lesen wir das nochmal aus und speichern es auch als release-Flag.
  const output = fs.readFileSync(process.env.GITHUB_OUTPUT, "utf-8");
  const match = output.match(/^version_changed=(.*)$/m);
  const value = match?.[1]?.trim() || "false";

  exportOutput("release", value);
  setEnv("VERSION_CHANGED", value);
}

main();
