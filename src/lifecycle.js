import { exec } from "node:child_process";

// Run operator-provided lifecycle commands (start/stop/restart). The commands
// come from env (MC_START_COMMAND / MC_STOP_COMMAND / MC_RESTART_COMMAND); they
// are never built from user input.
export function makeLifecycle({ start = "", stop = "", restart = "" } = {}) {
  const run = (cmd, label) =>
    new Promise((resolve, reject) => {
      if (!cmd) return reject(new Error(`${label} not configured`));
      exec(cmd, { timeout: 30000 }, (err, stdout, stderr) => {
        if (err) return reject(new Error(stderr.trim() || err.message));
        resolve({ ok: true, output: (stdout + stderr).trim() });
      });
    });

  return {
    canStart: () => Boolean(start),
    canStop: () => Boolean(stop),
    canRestart: () => Boolean(restart),
    start: () => run(start, "start"),
    stop: () => run(stop, "stop"),
    restart: () => run(restart, "restart"),
  };
}
