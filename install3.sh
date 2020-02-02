#!/bin/bash
cd matrix
echo "Running rgbmatrix installation..."
sudo apt-get update && sudo apt-get install python2.7-dev python-pillow -y
make build-python
sudo make install-python
cd bindings
sudo pip install -e python/
cd ../../
echo "Installing required dependencies. This may take some time (10-20 minutes-ish)..."
git reset --hard
git checkout master
git fetch origin --prune
git pull
sudo apt-get install libxml2-dev libxslt-dev
sudo pip3 install tzlocal urllib3
sudo pip3 install flask flask_restful python-dotenv gevent
sudo pip3 install ephem apscheduler
sudo pip3 install flask-cors --upgrade
make
echo "If you didn't see any errors above, everything should be installed!"
echo "Installation complete! Play around with the examples in matrix/bindings/python/samples to make sure your matrix is working."