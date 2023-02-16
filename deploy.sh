gcloud functions deploy check-messages \
--gen2 \
--region=us-east4 \
--runtime=python39 \
--source=. \
--entry-point=check_messages \
--trigger-topic=cherry-run