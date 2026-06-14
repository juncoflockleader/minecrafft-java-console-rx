import fs from "node:fs";
import { EventEmitter } from "node:events";

/**
 * Tails a growing log file by polling its size and reading appended bytes.
 * Polling (vs fs.watch) is reliable across platforms and survives log rotation
 * (when the file shrinks, we reset to the start of the new file).
 * Emits "line" for each appended line. Keeps a ring buffer of recent lines.
 */
export class LogTailer extends EventEmitter {
  constructor(filePath, { intervalMs = 500, historyLimit = 300 } = {}) {
    super();
    this.filePath = filePath;
    this.intervalMs = intervalMs;
    this.historyLimit = historyLimit;
    this.offset = 0;
    this.pending = "";
    this.history = [];
    this.timer = null;
  }

  start() {
    if (!this.filePath) return this;
    try {
      this.offset = fs.statSync(this.filePath).size; // start at end; only stream new lines
    } catch {
      this.offset = 0;
    }
    this.timer = setInterval(() => this._poll(), this.intervalMs);
    if (this.timer.unref) this.timer.unref();
    return this;
  }

  stop() {
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
  }

  getHistory() {
    return this.history.slice();
  }

  _poll() {
    let size;
    try {
      size = fs.statSync(this.filePath).size;
    } catch {
      return; // file may be momentarily absent during rotation
    }
    if (size < this.offset) this.offset = 0; // truncated/rotated
    if (size === this.offset) return;

    const stream = fs.createReadStream(this.filePath, { start: this.offset, end: size - 1 });
    let data = "";
    stream.on("data", (c) => (data += c));
    stream.on("end", () => {
      this.offset = size;
      this.pending += data;
      const lines = this.pending.split("\n");
      this.pending = lines.pop() ?? "";
      for (const line of lines) this._emitLine(line);
    });
    stream.on("error", () => {});
  }

  _emitLine(line) {
    this.history.push(line);
    if (this.history.length > this.historyLimit) this.history.shift();
    this.emit("line", line);
  }
}
