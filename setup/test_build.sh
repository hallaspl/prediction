if [ $1 ]
then 
   MESSAGE=$1
else
   MESSAGE="[>>TestBuild<<]"
fi

echo "$MESSAGE pip install -r requirements/development.txt"
pip install -r requirements/development.txt

echo "$MESSAGE pip install ."
pip install -e .
