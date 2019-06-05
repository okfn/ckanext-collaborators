#!/bin/sh
set -e

echo "This is travis-build.bash..."

echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install solr-jetty

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
if [ $CKANVERSION == 'master' ]
then
    echo "CKAN version: master"
else
    CKAN_TAG=$(git tag | grep ^ckan-$CKANVERSION | sort --version-sort | tail -n 1)
    git checkout $CKAN_TAG
    echo "CKAN version: ${CKAN_TAG#ckan-}"
fi

python setup.py develop
pip install -r requirements.txt --allow-all-external
pip install -r dev-requirements.txt --allow-all-external
cd -

echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'
sudo -u postgres psql -c "CREATE USER datastore_read WITH PASSWORD 'pass' NOSUPERUSER NOCREATEDB NOCREATEROLE;"
sudo -u postgres psql -c "CREATE USER datastore_write WITH PASSWORD 'pass' NOSUPERUSER NOCREATEDB NOCREATEROLE;"
sudo -u postgres psql -c 'CREATE DATABASE datastore_test WITH OWNER ckan_default;'


echo "SOLR config..."
# Solr is multicore for tests on ckan master, but it's easier to run tests on
# Travis single-core. See https://github.com/ckan/ckan/issues/2972
sed -i -e 's/solr_url.*/solr_url = http:\/\/127.0.0.1:8983\/solr/' ckan/test-core.ini
echo -e "NO_START=0\nJETTY_HOST=127.0.0.1\nJETTY_PORT=8983\nJAVA_HOME=$JAVA_HOME" | sudo tee /etc/default/jetty
echo "Files is:"
cat /etc/default/jetty
sudo cp ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
echo "Starting jetty"
sudo service jetty restart


echo "Initialising the database..."
cd ckan
paster db init -c test-core.ini
paster --plugin=ckanext-datastore datastore set-permissions -c test-core.ini | sudo -u postgres psql
cd -

echo "Installing ckanext-collaborators and its requirements..."
python setup.py develop
paster --plugin=ckanext-collaborators collaborators init-db -c ckan/test-core.ini

echo "Moving test.ini into a subdir..."
mkdir subdir
mv test.ini subdir

echo "travis-build.bash is done."
