# Chatbot-Messenger-in-Ecommerce

## 1. Prerequisites

- Python: 3.8.x

## 2. Environtment Setup

- Step 1: Clone project

  ```bash
  git clone https://github.com/tungnkhust/Chatbot-Messenger-in-Ecommerce.git
  ```

- Step 2: Change directory

  ```bash
  cd chatbot-messenger-in-ecommerce
  ```

- Step 3: Create venv

  ```bash
  python -m venv ./.venv
  ```

- Step 4: Activate venv

  ```bash
  # Window PowerShell
  ./.venv/bin/Activate.ps1

  # Linux
  source ./.venv/bin/activate
  ```

- Step 5: Install Python packages

  ```bash
  pip install -r requirements.txt
  ```

# Run weibot

Step 1:

- Collected `secret` and `page-access-token` on facebook app and add to `credentials.yml`
- Set field `verify` with any string to verify webhook

Step 2: run rasa service

```commandline
rasa run --endpoints endpoints.yml --credentials credentials.yml
```

Step 2: run ngrok to map local address to internet

```commandline
ngrok http 5005
```

Step 3: Add url after mapping of ngrok with format to facebook app:

`https://<host>:<port>/webhooks/facebook/webhook`
