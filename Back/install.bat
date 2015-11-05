:: ecoReleve-Sensor installation script
:: Requires Python 3.4.1, conda and conda-build
:: Minimum version of Pandas should be 0.15.0
conda install pandas=0.15.0
conda install pyodbc
conda install reportlab
conda install scikit-learn
conda install sqlalchemy
conda install zope.interface
conda install pywin32
conda install pycrypto
pip install jwt
pip install pyramid_jwtauth

python setup.py develop

cd ../Front
npm install
bower install
grunt dev

