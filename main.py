import os
import sys
from time import sleep
import requests
import json
from pathlib import Path
import logging
from urllib.parse import urlencode
import yaml
import argparse

parser = argparse.ArgumentParser(description="Read config file path")
parser.add_argument(
    "--config",
    type=str,
    default="config.json",
    help="Path to the configuration file"
)
parser.add_argument('--delete', action='store_true')
parser.add_argument('--info', action='store_true')
args = parser.parse_args()

with open(args.config, "r") as f:
    config = json.load(f)

LOG_FILENAME = config["log_filename"]
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    filename=LOG_FILENAME,
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger().addHandler(logging.StreamHandler())

def is_api_available():
    url_path = "/api/v0/auth/test"
    response = requests.request(
        "POST",
        config["tensordock"]["api_url"] + url_path,
        data = {
            'api_key': config["tensordock"]["api_key"],
            'api_token': config["tensordock"]["api_token"]
        }
    )
    sleep(1)
    data = json.loads(response.text)
    return data["success"]

def get_host_nodes():
    url_path = "/api/v0/client/deploy/hostnodes"
    response = requests.request(
        "GET",
        config["tensordock"]["api_url"] + url_path,
    )
    sleep(1)
    return json.loads(response.text)

def is_host_eligible(host):

    if not host["status"]["online"] or \
       host["specs"]["cpu"]["amount"] == 0:
        return False

    for host_config in config["host_configs"]:

        logging.debug(f"Test RAM: %s" % (host_config["ram"] <= int(host["specs"]["ram"]["amount"])))
        logging.debug(f"Test hdd: %s" % (host_config["hdd"] <= int(host["specs"]["storage"]["amount"])))
        logging.debug(f"Test gpu model: %s" % (host_config["gpu_model"] in host["specs"]["gpu"].keys()))

        if host_config["gpu_model"] in host["specs"]["gpu"].keys():

            logging.debug(f"Test gpu amount: %s" % (host_config["gpu_count"] <= host["specs"]["gpu"][host_config["gpu_model"]]["amount"]))
            logging.debug(f"Test ports: %s" % (len(host_config["internal_ports"]) <= len(host["networking"]["ports"])))

            if host_config["ram"] <= host["specs"]["ram"]["amount"]                                  and \
                host_config["hdd"] <= host["specs"]["storage"]["amount"]                             and \
                host_config["gpu_model"] in host["specs"]["gpu"].keys()                             and \
                host_config["gpu_count"] <= host["specs"]["gpu"][host_config["gpu_model"]]["amount"] and \
                len(host_config["internal_ports"]) <= len(host["networking"]["ports"]):
                return host_config

    # host is not eligible
    return False

def deploy_machine(host, host_config):

    url_path = "/api/v0/client/deploy/single"
    num_ports = len(host_config["internal_ports"])

    payload = {
        'api_key': config["tensordock"]["api_key"],
        'api_token': config["tensordock"]["api_token"],
        'password': host_config["password"],
        'name': host_config["name"],
        'gpu_count': host_config["gpu_count"],
        'gpu_model': host_config["gpu_model"],
        'vcpus': host_config["vcpus"],
        'ram': host_config["ram"],
        'external_ports': str(set(host["networking"]["ports"][:num_ports])),
        'internal_ports': str(set(host_config["internal_ports"])),
        'hostnode': host["id"],
        'storage': host_config["hdd"],
        'operating_system': host_config["os"]
    }

    if "cloudinit_file" in host_config and \
        os.path.isfile(host_config["cloudinit_file"]):
        with open(host_config["cloudinit_file"], 'r') as f:
            payload["cloudinit_script"] = f.read().replace('\n', r'\n')

    logging.debug("Deploying machine")
    logging.debug(host)
    logging.debug("---")
    logging.debug(payload)
    logging.debug("===")

    req = requests.Request(
        "POST",
        config["tensordock"]["api_url"] + url_path,
        headers = {},
        data = payload
    )
    prepared = req.prepare()

    def pretty_print_POST(req):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in
        this function because it is programmed to be pretty
        printed and may differ from the actual request.
        """
        print('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))

    pretty_print_POST(prepared)

    response = requests.Session().send(prepared)
    logging.debug(response.text)
    data = json.loads(response.text)
    success = data["success"]
    sleep(1)

    ssh_port = 0
    if success:
        logging.info("Machine deployed")
        http_port = 0
        for port in data["port_forwards"]:

            if int(data["port_forwards"][port]) == 22:
                ssh_port = int(port)
                logging.info(f"ssh-keygen -f $HOME/.ssh/known_hosts -R '[%s]:%i'" % (data["ip"], ssh_port))
                logging.info(f"ssh -o StrictHostKeyChecking=accept-new -p %i user@%s" % (ssh_port, data["ip"]))
                logging.info(f"ssh -o StrictHostKeyChecking=accept-new -p %i user@%s 'sudo tail -f /var/log/cloud-init-output.log'" % (ssh_port, data["ip"]))

            if int(data["port_forwards"][port]) in [8888, 5000]:
                http_port = int(port)
                logging.info(f"http://%s:%i" % (data["ip"], http_port))

    return ssh_port

def info_deploys():

    url_path = "/api/v0/client/list"
    response = requests.request(
        "POST",
        config["tensordock"]["api_url"] + url_path,
        data = {
            'api_key': config["tensordock"]["api_key"],
            'api_token': config["tensordock"]["api_token"]
        }
    )
    sleep(1)
    response = json.loads(response.text)

    for server_uuid in response["virtualmachines"]:

        url_path = "/api/v0/client/get/single"
        response = requests.request(
            "POST",
            config["tensordock"]["api_url"] + url_path,
            data = {
                'api_key': config["tensordock"]["api_key"],
                'api_token': config["tensordock"]["api_token"],
                'server': server_uuid
            }
        )
        response = json.loads(response.text)
        logging.debug(response)
        sleep(1)

def delete_deploys():

    url_path = "/api/v0/client/list"
    response = requests.request(
        "POST",
        config["tensordock"]["api_url"] + url_path,
        data = {
            'api_key': config["tensordock"]["api_key"],
            'api_token': config["tensordock"]["api_token"]
        }
    )
    sleep(1)
    response = json.loads(response.text)

    for server_uuid in response["virtualmachines"]:

        url_path = "/api/v0/client/delete/single"
        response = requests.request(
            "POST",
            config["tensordock"]["api_url"] + url_path,
            data = {
                'api_key': config["tensordock"]["api_key"],
                'api_token': config["tensordock"]["api_token"],
                'server': server_uuid
            }
        )
        sleep(1)

# Modify the deploy_node() function to focus on specific locations
def deploy_node():
    while True:
        hosts = get_host_nodes()
        host_nodes_keys = hosts["hostnodes"].keys()

        chosen_host = None
        for key in host_nodes_keys:
            host = hosts["hostnodes"][key]
            if host["location"]["country"] in ["Poland", "Estonia", "Sweden", "Germany", "Netherlands", "France", "Luxembourg", "Czech Republic", "CzechRepublic", "Czech_Republic", "Switzerland", "Austria", "Ukraine", "Norway", "United_Kingdom", "UK", "United Kingdom", "Belgium", "Denmark", "Lithuania", "Slovakia", "Hungary", "Russia", "Italy", "Slovenia"]:
                host_config = is_host_eligible(host)
                if host_config:
                    host["id"] = key
                    chosen_host = host
                    break

        if chosen_host:
            ssh_port = deploy_machine(chosen_host, host_config)
            if ssh_port != 0:
                logging.debug("Machine deployed successfully.")
                break  # Exit the loop if deployment is successful
        else:
            logging.debug("No eligible host found in specified countries / cities. Retrying in 60 seconds.")
            sleep(60)  # Retry after 60 seconds if no eligible host is found in the specified locations


    if host["id"] is not None:
        ssh_port = deploy_machine(host, host_config)

        # if ssh_port != 0:

        #     while True:
        #         try:
        #             ssh.connect(ip, username=user, key_filename=key_file)
        #             break
        #         except (BadHostKeyException, AuthenticationException, SSHException, socket.error) as e:
        #             logging.debug(e)
        #             sleep(2)

if is_api_available():
    if args.delete:
        delete_deploys()
    elif args.info:
        info_deploys()
    else:
        deploy_node()
else:
    logging.info("API not available")
