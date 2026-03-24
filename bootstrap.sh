#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p local
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install --config-settings editable_mode=strict --group dev --editable .
clk install
