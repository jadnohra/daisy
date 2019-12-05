virtualenv --python=$(which python3) venv
virtualenv --python=$(which python3) venv_jupyter
source ./activate_venv.sh
pip install -r ./requirements.txt
deactivate
