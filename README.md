```gcloud builds submit --tag eu.gcr.io/cj-growth/crawl-matchi```

```gcloud run deploy crawl-matchi --image eu.gcr.io/cj-growth/crawl-matchi --platform managed --memory 2G --cpu 2```

# Replace uri
```gcloud scheduler jobs create http crawl-matchi --schedule="*/19 * * * *" --uri="https://*.run.app/" --http-method=GET --time-zone="CET" --attempt-deadline="600s" --location europe-west1 --description="Invokes crawl matchi"```
