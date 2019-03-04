#!/usr/bin/env bash
set -e

if [[ -z "${B_PLUGIN}" ]]; then
  echo "Environment B_PLUGIN is not defined"
  exit 1
fi

pip install $B_PLUGIN --process-dependency-links