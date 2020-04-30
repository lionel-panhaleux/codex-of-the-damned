deploy:
	rsync -rptovzFF --delete-after -e ssh . krcg.org:projects/codex-of-the-damned.org/dist/