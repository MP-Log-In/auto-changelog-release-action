const cp = require("child_process");
const path = require("path");

function run(script, args = []) {
  const cmd = typeof script === "string" ? script : script.join(" ");
  cp.execSync(cmd, {
    stdio: "inherit",
    shell: true,
    env: process.env,
  });
}

function scriptPath(...segments) {
  return path.join(__dirname, "..", "scripts", ...segments);
}

function main() {
  const versionChanged = (process.env.VERSION_CHANGED || "false").toLowerCase() === "true";

  const readCliffScript = scriptPath("read-cliff-version.sh");
  const cliffVersion = cp
    .execSync(readCliffScript, { encoding: "utf-8", shell: true })
    .trim()
    .split("\n")
    .pop();

  run(scriptPath("install-git-cliff.sh") + " " + cliffVersion);

  run(
    scriptPath("setup-git.sh") +
      ` "${process.env.INPUT_AUTHOR_NAME}" "${process.env.INPUT_AUTHOR_EMAIL}"`
  );

  if (versionChanged) {
    process.env.RELEASE_PUBLISH_TOKEN = process.env.INPUT_TOKEN || "";
    run(scriptPath("release-from-version.sh"));
  } else {
    run(scriptPath("generate-unreleased-changelog.sh"));
  }
}

main();
