#!/bin/bash

hook_path="./.git/hooks/pre-commit"

if ! [ -f $hook_path ]; then
  echo "pre-commit does not exist."
  poetry run pre-commit install
  echo "black ./colorcamp" >> $hook_path &&
  echo "isort ./colorcamp" >> $hook_path &&
  echo "mypy ./colorcamp" >> $hook_path &&
  echo "poetry run python lint.py -p ./colorcamp/" >> $hook_path &&
  chmod +x .git/hooks/pre-commit
fi
