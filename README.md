# Chatbot-Messenger-in-Ecommerce

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