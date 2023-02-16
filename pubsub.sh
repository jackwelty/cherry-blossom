gcloud scheduler jobs create pubsub cherry-trigger --schedule "*/10 * * * *" \
  --topic cherry-run --message-body "{'data': 'example-message'}" --location us-east4