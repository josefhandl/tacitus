#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

venv/bin/python -m uvicorn api.main:app --reload --host=0.0.0.0 --port=8155

