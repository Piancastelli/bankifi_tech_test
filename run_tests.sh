function cleanup {
	echo "Deactivating environment"
	deactivate
	echo "Removing virtualenv"
	rm -rf test_env
}

trap cleanup SIGINT SIGKILL EXIT

echo "Creating virtualenv called 'test_env'"
virtualenv test_env

echo "Activating virtualenv"
source test_env/bin/activate

echo "Installing required packages"
pip install .

echo "Running tests"
nosetests -v test_saucedemo.py

