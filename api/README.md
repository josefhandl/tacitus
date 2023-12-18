## Run API
Start by `python -m uvicorn api.main:app --reload --host=0.0.0.0 --port=8000` in VENV and go to `http://127.0.0.1:8000/docs`.

### Ignoring modules
Use `TACITUS_IGNORE_MODULES` environment variable to ignore modules. For example, to ignore `power` and `smartctl` modules, run:
`TACITUS_IGNORE_MODULES=power,smartctl ./run_api.sh `

### Formating
`black api -l 120`