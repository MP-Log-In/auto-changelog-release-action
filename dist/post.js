const cp = require("child_process");
const path = require("path");

function run(script, args = []) {
  cp.execFileSync(script, {
    stdio: "inherit",
    shell: true,
    env: process.env,
  });
}

function main() {
  const actionPath = process.env.GITHUB_ACTION_PATH || ".";
  const versionChanged = (process.env.VERSION_CHANGED || "false").toLowerCase() === "true";

  const readCliff = path.join(actionPath, "scripts/read-cliff-version.sh");
  const cliffVersion = cp.execSync(readCliff, { encoding: "utf-8", shell: true }).trim().split("\n").pop();

  run(path.join(actionPath, "scripts/install-git-cliff.sh"), [cliffVersion]);

  run(`${path.join(actionPath, "scripts/setup-git.sh")} "${process.env.INPUT_AUTHOR_NAME}" "${process.env.INPUT_AUTHOR_EMAIL}"`);

  if (versionChanged) {
    process.env.RELEASE_PUBLISH_TOKEN = process.env.INPUT_TOKEN || "";
    run(path.join(actionPath, "scripts/release-from-version.sh"));
  } else {
    run(path.join(actionPath, "scripts/generate-unreleased-changelog.sh"));
  }
}

main();
