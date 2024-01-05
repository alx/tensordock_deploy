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
    - host_configs `[priority]` level allows for the script to choose the nicest setup

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
      "priority": 1,
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
      "priority": 2,
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
    "Germany", "Poland", "Czech Republic", "Netherlands", "Belgium", 
    "Denmark", "France", "Switzerland", "Austria", "Luxembourg", 
    "Sweden", "Slovenia", "Italy", "Hungary", "Slovakia", 
    "Estonia", "Finland", "United Kingdom", "UK", "United_Kingdom", 
    "Norway", "Lithuania", "Portugal", "Ukraine", "Russia",
]


# Telegram bot details
bot_token = 'YOUR BOT TOKEN'
chat_id = '-YOUR CHAT ID'
bot = Bot(token=bot_token)

async def send_notification(location, gpu_name, gpu_quantity, ram, cpu, storage):
    gpu_types = {
        "rtx3090": "RTX 3090 24GB",
        "rtx3080ti": "RTX 3080 Ti 12GB",
        "rtx3060ti": "RTX 3060 Ti 8GB",
        "gtx1070": "GTX 1070 8GB",
        "rtx4090": "RTX 4090 24GB",
        "a6000": "RTX A6000 48GB",
        "a4000": "RTX A4000 16GB",
        "a100": "A100 80GB",
        "l40": "L40 48GB"
        # Add other GPU types here
    }

    formatted_gpu_name = None

    for gpu_type, formatted_name in gpu_types.items():
        if gpu_type in gpu_name.lower():
            formatted_gpu_name = formatted_name
            break

    if formatted_gpu_name is None:
        formatted_gpu_name = gpu_name  # Default to the original name if no match is found

    message = (
        f"New GPU server deployed\n"
        f"GPU type: {formatted_gpu_name}\n"
        f"GPU quantity: {gpu_quantity}\n"
        f"RAM: {ram} GB\n"
        f"CPU: {cpu} Cores\n"
        f"Storage: {storage} GB SSD\n"
        f"Login at https://marketplace.tensordock.com/list"
    )

    await bot.send_message(chat_id=chat_id, text=message)

