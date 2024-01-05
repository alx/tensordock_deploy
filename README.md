# `tensordock_deploy_CC`

Script to deploy a VM on `marketplace.tensordock.com` using API.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/alx/tensordock_deploy.git
    cd tensordock_deploy
    ```

2. Set up the environment:

    ```sh
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt

    cp config.json.sample config.json
    cp cloud_init.yml.sample cloud_init.yml
    ```

## Configuration

- Edit `config.json`:
    - Replace `TENSORDOCK_API_KEY`, `TENSORDOCK_API_TOKEN`, `VM_NAME`, and `VM_PASSWORD`.
    - Adjust `host_configs` to set the deployment parameters.

    Example `config.json`:

    ```json
    {
      "tensordock": {
        "api_key": "YOUR_API_KEY",
        "api_token": "YOUR_API_TOKEN",
        "api_url": "https://marketplace.tensordock.com"
      },
      "VM_NAME": "Your_VM_Name",
      "VM_PASSWORD": "Your_VM_Password",
      "host_configs": [
        {
          "priority": 1,
          "ram": 16,
          "hdd": 200,
          "gpu_model": "RTX 3090",
          "gpu_count": 1,
          "vcpus": 4,
          "internal_ports": [22, 80],
          "password": "Your_VM_Password",
          "os": "ubuntu",
          "cloudinit_file": "path/to/cloud-init-file.yml"
        }
      ]
    }
    ```

## Telegram Integration

- To enable Telegram notifications:
    - Replace `bot_token` and `chat_id` variables with your Telegram Bot token and chat ID.
    - Use the `async def send_notification()` function to customize the message content and triggers.

Example:

```python
# Replace 'bot_token' and 'chat_id' with your Telegram Bot token and chat ID
bot_token = 'YOUR_BOT_TOKEN'
chat_id = 'YOUR_CHAT_ID'

async def send_notification(location, gpu_name, gpu_quantity, ram, cpu, storage):
    # Customize the message content here
    message = (
        f"New GPU server deployed\n"
        f"GPU type: {gpu_name}\n"
        f"GPU quantity: {gpu_quantity}\n"
        f"RAM: {ram} GB\n"
        f"CPU: {cpu} Cores\n"
        f"Storage: {storage} GB SSD\n"
        f"Login at https://marketplace.tensordock.com/list"
    )

    await bot.send_message(chat_id=chat_id, text=message)
