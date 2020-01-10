#!/usr/bin/env bash

# The "codex" SFTP has to be properly configured in ~/.ssh/config

# path of the remote public website folder
WWW_PATH="www"

echo "get commit.hash" | sftp codex
echo "cd ${WWW_PATH}" > batch_update
for f in $(git diff `cat commit.hash` HEAD --name-only); do echo "put $f `dirname $f`" >> batch_update; done
sftp -b batch_update codex
rm batch_update
git rev-parse HEAD > commit.hash
echo "put commit.hash" | sftp codex
rm commit.hash
