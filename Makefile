deploy:
	rsync -rptovzFF --delete-after -e ssh . krcg:projects/codex-of-the-damned.org/dist/