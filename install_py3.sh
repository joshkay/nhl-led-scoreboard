#!/bin/bash
# Use this install script for python3
cd matrix || exit
echo "Running rgbmatrix installation..."
sudo apt-get update && sudo apt-get install python3-dev python3-pillow -y
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
cd bindings
sudo pip3 install -e python/
cd ../../
echo "Installing required dependencies. This may take some time (10-20 minutes-ish)..."
git reset --hard
git checkout master
git fetch origin --prune
git pull
sudo pip3 install requests
sudo pip3 install flask flask_restful python-dotenv gevent
sudo pip3 install ephem apscheduler
sudo pip3 install flask-cors --upgrade
make
echo "If you didn't see any errors above, everything should be installed!"
echo "Installation complete! Play around with the examples in matrix/bindings/python/samples to make sure your matrix is working."
