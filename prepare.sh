cd $(dirname ${BASH_SOURCE[0]})
if [ ! -d venv ]; then python3 -m venv venv --prompt "TacitusVENV" ; fi
source venv/bin/activate
python -m pip install -r requirements.txt
cd  -