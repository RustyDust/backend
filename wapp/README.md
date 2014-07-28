## Installation

```
apt-get install mysql-server python-mysqldb
echo 'CREATE DATABASE mqttitude;' | mysql -u root

pip install -r requirements.txt
cp config.example owntracks.cfg
vi owntracks.cfg
```


## Running

```
./run.sh
```