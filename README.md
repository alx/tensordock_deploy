# tensordock_deploy_CC 🚀

Script to deploy a VM on `marketplace.tensordock.com` using API.

Filters by County or City and notifies you via Telegram 🌍.

## Installation 💻

1. Clone the repository:

    ```sh
    git clone https://github.com/ULTRA-VAGUE/tensordock_deploy_CC.git
    cd tensordock_deploy_CC
    ```

2. Set up the environment:

    ```sh
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt

    cp config.json.sample config.json
    cp cloud_init.yml.sample cloud_init.yml
    ```

## VM Configuration ⚙️

- Edit `config.json`:
    - Replace `TENSORDOCK_API_KEY`, `TENSORDOCK_API_TOKEN`, `VM_NAME`, and `VM_PASSWORD`.
    - Adjust `host_configs` to set the deployment parameters.

    Example `config.json`:

    ```json
    {
  "log_filename": "log.txt",
  "tensordock": {
    "api_url": "https://marketplace.tensordock.com",
    "api_key": "TENSORDOCK_API_KEY",
    "api_token": "TENSORDOCK_API_TOKEN"
  },
  "host_configs": [
    {
      "gpu_count": 1,
      "gpu_model": "rtxa4000-pcie-16gb",
      "ram": 16,
      "vcpus": 4,
      "hdd": 70,
      "internal_ports": [
        22,
        8888,
        5000
      ],
      "os": "Ubuntu 22.04 LTS",
      "password": "VM_PASSWORD",
      "name": "VM_NAME",
      "cloudinit_file": "cloud_init.yml"
    },
    {
      "gpu_count": 1,
      "gpu_model": "geforcertx4090-pcie-24gb",
      "ram": 16,
      "vcpus": 4,
      "hdd": 70,
      "internal_ports": [
        22,
        8888,
        5000
      ],
      "os": "Ubuntu 22.04 LTS",
      "password": "VM_PASSWORD",
      "name": "VM_NAME",
      "cloudinit_file": "cloud_init.yml"
    }
  ]

# Available GPU Flags 🚩

- `a100-pcie-80gb` // A100 80 GB
- `geforcegtx1070-pcie-8gb` // GTX 1070 8 GB
- `geforcertx3060ti-pcie-8gb` // RTX 3060 8 GB
- `geforcertx3090-pcie-24gb` // RTX 3090 24 GB
- `geforcertx4090-pcie-24gb` // RTX 4090 24 GB
- `l40-pcie-48gb` // L 40 48GB
- `rtxa4000-pcie-16gb` // RTX A4000 16 GB
- `rtxa5000-pcie-24gb` // RTX A5000 24 GB
- `rtxa6000-pcie-48gb` // RTX A6000 48 GB

## Script Setup | Telegram Integration 📲
- Add your desired countries or cities
    - To make sure you don´t miss one of your countries or cities, use every possible spelling.
        - e.g.  UK, United_Kingdom, United Kingdom, UnitedKingdom
     

- To enable Telegram notifications:
    - Replace `bot_token` and `chat_id` variables with your Telegram Bot token and chat ID.
    - Use the `async def send_notification()` function to customize the message content and triggers.

Example:

```python
# List of countries
eligible_countries = [
    "Poland", "Estonia", "Sweden", "Germany", "Netherlands", 
    "France", "Luxembourg", "Czech Republic", "CzechRepublic", 
    "Czech_Republic", "Switzerland", "Austria", "Ukraine", 
    "Norway", "United_Kingdom", "UK", "United Kingdom", 
    "Belgium", "Denmark", "Lithuania", "Slovakia", "Hungary", 
    "Russia", "Italy", "Slovenia", "Finland", "Spain", "Portugal",
]

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
