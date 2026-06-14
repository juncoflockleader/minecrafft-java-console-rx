import { exec } from "node:child_process";

// Run the configured restart command (e.g. a launchctl kickstart). The command
// is operator-provided via MC_RESTART_COMMAND; we never build it from user input.
export function makeLifecycle(restartCommand) {
  return {
    available: () => Boolean(restartCommand),
    restart() {
      return new Promise((resolve, reject) => {
        if (!restartCommand) return reject(new Error("restart not configured (set MC_RESTART_COMMAND)"));
        exec(restartCommand, { timeout: 30000 }, (err, stdout, stderr) => {
          if (err) return reject(new Error(stderr.trim() || err.message));
          resolve({ ok: true, output: (stdout + stderr).trim() });
        });
      });
    },
  };
}
