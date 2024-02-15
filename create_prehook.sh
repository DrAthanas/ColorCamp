#!/bin/bash

hook_path="./.git/hooks/pre-commit"

if ! [ -f $hook_path ]; then
  echo "pre-commit does not exist."
  echo "black ./colorcamp" > $hook_path &&
  echo "mypy ./colorcamp" >> $hook_path &&
  echo "isort ./colorcamp" >> $hook_path &&
  echo "python lint.py -p ./colorcamp/" >> $hook_path
  chmod +x .git/hooks/pre-commit
fi
