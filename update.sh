#!/usr/bin/env bash

# The "codex" SFTP has to be properly configured in ~/.ssh/config

# path of the remote public website folder
WWW_PATH="www"

echo "get commit.hash" | sftp codex
echo "cd ${WWW_PATH}" > batch_update
echo "cd ${WWW_PATH}" > batch_delete
git diff `cat commit.hash` HEAD --name-status | while read line; do
    stat_path=($line)
    mod=${stat_path[0]}
    if [ "${stat_path[0]}" == "D" ]; then
        echo "rm ${stat_path[1]}" >> batch_delete;
    elif [[ "${stat_path[0]}" == "R"* ]]; then
        echo "rm ${stat_path[1]}" >> batch_delete;
        echo "put ${stat_path[2]} `dirname ${stat_path[2]}`" >> batch_update;
    else
        echo "put ${stat_path[1]} `dirname ${stat_path[1]}`" >> batch_update;
    fi
done
sftp -b batch_update codex
sftp -b batch_delete codex
rm batch_update
rm batch_delete
git rev-parse HEAD > commit.hash
echo "put commit.hash" | sftp codex
rm commit.hash
