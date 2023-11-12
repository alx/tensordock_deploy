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

## examples

### Real-Time-Latent-Consistency-Model

```sh
cd tensordock_deploy
cp config.rtlcm.json config.json
cp cloud-init.rtlcm.yml cloud-init.yml
```

1. Edit `config.json` with Tensordock marketplace API tokens from https://marketplace.tensordock.com/api
2. Edit `config.json` to change `VM_NAME` and `VM_PASSWORD`
3. Edit `cloud-init.yml` with Tailscale `authkey` with ephemeral+reusable key issued from https://login.tailscale.com/admin/settings/keys

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Wait for `cloud-init` to finish VM setup:

```sh
ssh -o StrictHostKeyChecking=accept-new -p SSH_PORT user@MACHINE_IP 'sudo tail -f /var/log/cloud-init-output.log'"
```

Connect to machine VM using ssh and fix ssl port in `$HOME/rtlcm/main.py`:

```sh
ssh -o StrictHostKeyChecking=accept-new -p SSH_PORT user@MACHINE_IP
$ nano rtlcm/main.py
$ killall python3
$ source /home/user/.venv/bin/activate && python3 /home/user/rtlcm/main.py 
```

