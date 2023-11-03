# tensordock_deploy

Script to deploy VM on marketplace.tensordock.com using API

## install

``` sh
git clone https://github.com/alx/tensordock_deploy.git
cd tensordock_deploy

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp config.json.sample config.json
cp clound_init.yml. sample cloud_init.yml
```

## config

In `config.json`, replace `TENSORDOCK_API_KEY`, `TENSORDOCK_API_TOKEN`, `VM_NAME` and `VM_PASSWORD`

`host_configs[priority]` level allow script to choose the nicest setup

## run

### start a new VM

``` sh
python3 main.py
```

### delete running VM

``` sh
python3 main.py --delete
```

### get info on running VM

``` sh
python3 main.py --info
```
