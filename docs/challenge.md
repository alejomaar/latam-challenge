docker build -t challenge .
docker run -d challenge -p 4000:4000

gcloud run deploy latam-challenge --source . --platform managed --region us-east1 --allow-unauthenticated
gcloud run deploy latam-challenge --source . --platform managed --region us-central1 --allow-unauthenticated --service-account=access@dataflow-416921.iam.gserviceaccount.com

ENV PORT 8080

gcloud run deploy latam-challenge \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --service-account deployment-service-account@latam-challenge-436723.iam.gserviceaccount.com
