# Wetbot-Messenger-in-Ecommerce

## 1. Prerequisites

- Python: 3.8.8

## 2. Environment Setup

- Step 1: Clone project
  
  ```bash
  git clone git@github.com:tungnkhust/Weibot-Chatbot-Messenger-in-Ecommerce.git
  ```

- Step 3: Create env
  ```bash
  cp .env.example .env
  ```
  ```bash
  export PYTHONPATH=./
  ```

- Step 4: Install Python packages

  ```bash
  pip install -r requirements.txt
  ```
  If install rasa slowly you can install  pip with version: 20.2
  ```bash
  pip install --upgrade pip==20.2 
  ```
# Run weibot
### Step 1: Set config
#### Credentials
- Collected `secret` and `page-access-token` on facebook app and add to file `credentials.yml`
- Set field `verify` with any string to verify webhook
```yaml
facebook:
  verify: "rasa"
  secret: "secret"
  page-access-token: "page-access-token"

```

### Step 2: Run rasa service
```bash
rasa run --endpoints endpoints.yml --credentials credentials.yml
```
Note: Before run service, you must provide model. You can train model with command line:
```bash
rasa train -c config.yml -d domain.yml 
```

### Step 3: Run rasa action server
```bash
rasa run actions --debug
```

### Step 4: Connect to facebook messenger channel
- Run ngrok to map local port 5005 (rasa) to public port:
```bash
ngrok http 5005
```
- Add url(https) after mapping of ngrok with format to facebook app:
`https://<host>:<port>/webhooks/facebook/webhook` in messenger setting of facebook app.
When add url, facebook request verify url, you can pass `verify` in `credentials.yml`.