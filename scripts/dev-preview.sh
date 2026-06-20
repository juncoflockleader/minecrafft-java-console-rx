#!/usr/bin/env bash
export HOST=127.0.0.1 PORT=8799 RCON_PASSWORD=preview CLIENT_MODS_DIR=/tmp/test-clientmods MC_GAME_VERSION=1.21.11
exec node src/server.js
