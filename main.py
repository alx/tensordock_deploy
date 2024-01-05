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
from aiogram import Bot, types
import asyncio
from plyer import notification
import webbrowser

# List of countries
eligible_countries = [
    "Germany", "Poland", "Czech Republic", "CzechRepublic", "Czech_Republic", "Netherlands", "Belgium", 
    "Denmark", "France", "Switzerland", "Austria", "Luxembourg", 
    "Sweden", "Slovenia", "Macedonia", "Italy", "Hungary", "Slovakia", 
    "Estonia", "Finland", "United Kingdom", "UK", "United_Kingdom", 
    "Norway", "Lithuania", "Portugal", "Ukraine", "Russia", "Spain",
]


# Telegram bot details, if empty, no notification will be sent
bot_token = 'YOUR BOT TOKEN'
chat_id = 'YOUR CHAT ID'

if bot_token.strip() and ' ' not in bot_token and chat_id.strip() and ' ' not in chat_id:
    print('Telegram bot enabled\n\n')
    wait = input('Press enter to continue...')
    bot = Bot(token=bot_token)
elif bot_token=='YOUR BOT TOKEN' and chat_id=='YOUR CHAT ID':
    print('Telegram bot disabled, please set your bot token and chat id\n\n')
    wait = input('Press enter to continue...')
    exit()


async def send_notification(location, gpu_name, gpu_quantity, ram, cpu, storage):
    gpu_types = {
        "rtx3090": "RTX 3090 24GB",
        "rtx3080ti": "RTX 3080 Ti 12GB",
        "rtx3060ti": "RTX 3060 Ti 8GB",
        "gtx1070": "GTX 1070 8GB",
        "rtx4090": "RTX 4090 24GB",
        "a6000": "RTX A6000 48GB",
        "a5000": "RTX A5000 24GB",
        "a4000": "RTX A4000 16GB",
        "a100": "A100 80GB",
        "l40": "L40 48GB"
        # Add other GPU types here for custom formatting in telegram notification
    }

    formatted_gpu_name = None

    for gpu_type, formatted_name in gpu_types.items():
        if gpu_type in gpu_name.lower():
            formatted_gpu_name = formatted_name
            break

    if formatted_gpu_name is None:
        formatted_gpu_name = gpu_name  # Default to the original name if no match is found

    message = (
        f"New GPU server deployed in {location}\n"
        f"GPU type: {formatted_gpu_name}\n"
        f"GPU quantity: {gpu_quantity}\n"
        f"RAM: {ram} GB\n"
        f"CPU: {cpu} Cores\n"
        f"Storage: {storage} GB SSD\n"
        f"Login at https://marketplace.tensordock.com/list"
    )

    await bot.send_message(chat_id=chat_id, text=message)




def desktop_notification(message):
    notification_title = "TensorDock Notification"
    notification_text = message
    notification_timeout = 10  # Notification will be displayed for 10 seconds

    notification.notify(
        title=notification_title,
        message=notification_text,
        timeout=notification_timeout,
        app_icon=None,  # You can specify an icon path if needed
    )
# if a GPU is found, open the marketplace page
    webbrowser.open('https://marketplace.tensordock.com/list')




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

while True:
    try:
        hosts = get_host_nodes()
        logging.debug(f"Available hosts: {hosts}")

        chosen_host = None
        for key, host in hosts["hostnodes"].items():
            if host["location"]["country"] in eligible_countries:
                host_config = is_host_eligible(host)
                if host_config:
                    host["id"] = key
                    chosen_host = host
                    break  # Exit the for loop if an eligible host is found

        if chosen_host:
            ssh_port = deploy_machine(chosen_host, host_config)
            if ssh_port != 0:
                logging.debug("Machine deployed successfully.")
                # Check for GPU server and trigger Telegram notification
                if host_config["gpu_model"]:
                    location = chosen_host["location"]["country"]
                    gpu_type = host_config["gpu_model"]
                    gpu_quantity = host_config["gpu_count"]
                    ram = host_config["ram"]
                    cpu = host_config["vcpus"]
                    storage = host_config["hdd"]
                    asyncio.run(send_notification(location, gpu_type, gpu_quantity, ram, cpu, storage))
                    desktop_notification("TensorDock GPU Server Available, login at https://marketplace.tensordock.com/list")
                break  # Exit the while loop if deployment is successful
        else:
            countries_without_eligible_hosts = [host["location"]["country"] for host in hosts["hostnodes"].values()
                                                if host["location"]["country"] not in eligible_countries]
            logging.info(f"No GPU server available in eligible countries: {eligible_countries}.")

            logging.debug(f"Retrying in 60 seconds.")
            sleep(60)  # Retry after 60 seconds if no eligible host is found in the specified locations

    except Exception as e:
        logging.exception(f"An exception occurred: {e}")
        logging.debug(f"Retrying in 60 seconds.")
        sleep(60)



    if "id" in host and host["id"] is not None:
        ssh_port = deploy_machine(host, host_config)

        # if ssh_port != 0:

        #     while True:
        #         try:
        #             ssh.connect(ip, username=user, key_filename=key_file)
        #             break
        #         except (BadHostKeyException, AuthenticationException, SSHException, socket.error) as e:
        #             logging.debug(e)
        #             sleep(2)

