python3 -m venv .
source bin/activate
pip3 install --upgrade pip
pip3 install pytest
pytest demoodle.py
pip3 install lxml
pip3 install bs4
pip3 install autopep8
autopep8 --in-place --aggressive --aggressive demoodle.py
