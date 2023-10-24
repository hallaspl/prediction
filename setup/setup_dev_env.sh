set -e

MESSAGE="[--EnvSetup--]"

echo "$MESSAGE python3.11 -m venv .venv"
python3.11 -m venv .venv

echo "$MESSAGE source .venv/bin/activate"
source .venv/bin/activate

./setup/test_build.sh $MESSAGE

echo "$MESSAGE pytest"
pytest

echo "$MESSAGE flake8"
flake8
