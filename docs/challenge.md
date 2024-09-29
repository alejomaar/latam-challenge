
# Flight Delay Prediction API - Solution
<p align="center">
    
  <i align="center">Software Engineer (ML & LLMs) Challenge - Solution by Alejandro Aponte🚀</i>
</p>


<p align="center">
    <img src="https://github.com/user-attachments/assets/9e9a155b-6cf4-4604-974c-4657eaf0265c" alt="dashboard"/>
</p>


## Introduction




This document outlines the deployment of a machine learning model aimed at predicting flight delays at SCL airport. The Data Science team created multiple models, and the most suitable one was selected based on performance. This model is integrated into a public API deployed on Cloud Run GCP and FastAPI.

The architecture of the solution is designed to manage high peak of request, extreamly fast API responses, and autoscalability. While mantaining a cost-effective solution.


#### Key Features

* **Fast:** The median API response time is consistently below 100 ms. *(See Locust Report).*
* **Data Validation:** Pydantic validation ensures data quality, meeting strict data quality constraints, e.g., validating MES as an integer between 1 and 12.
* **Cost-Effective:** Pay as you go. The billing is based on the number of requests being processed, so there's no need to allocate unnecessary resources.
* **Scalable:** Cloud Run automatically scales to handle fluctuating traffic demands.
* **CI:** When new code is pushed to a branch, both the model and the API must pass quality checks.
* **CD:** When code is merged to the main branch, it is automatically deployed to GCP, so you don’t need to manage deployments yourself.
* **Serverless:** Managing all the infrastructure ourselves is a challenging task (e.g., provisioning the VM, scalability, etc.). The Cloud Run solution handles all of this for us, allowing us to focus on development.
* **Integrated Documentation:** Pydantic and FastAPI are integrated to maintain high-quality documentation. Not only is the code documented, but when you run the FastAPI documentation, you can also see all the input/output schemas of the API.


#### Technology Stack
* **Backend (Python):**
    * FastAPI
    * NumPy
    * Pydantic
    * Uvicorn
    * Pandas
    * Scikit-learn
* **Infrastructure:**
    * GCP Cloud Run
    * GCP Artifact Registry
    * GCP IAM
* **CI/CD:**
    * Docker
    * GitHub Actions
 
#### API Endpoints

Here's a small documentation snippet for your API endpoints:

---

### API Endpoints

#### Health Check
- **Method:** `GET`
- **Endpoint:** `https://latam-challenge-693731259774.us-central1.run.app/`
- **Description:** Checks the health status of the API service.

#### Prediction
- **Method:** `POST`
- **Endpoint:** `https://latam-challenge-693731259774.us-central1.run.app/predict`
- **Description:** Sends data to the API for to obtain predictions.



## Part I: Model Development

* **Package Management:** Resolved package incompatibilities and added missing packages (e.g., XGBoost) to `requirements.txt`.  New packages were chosen to maintain compatibility with existing ones.
* **Model Selection:** After reducing the features to the 10 most important, It Does not decrease the performance of the model and balancing classes increases the recall of class "1". It let us with 2 models, XGBoost and  Logistic Regression. Both have extremely similar performance metrics, but Logistic Regression is much simplier and interpretable than XGBoost, so `Logistic Regression with feature importance and balanced data` is the selected model.

* **Model Training/Inference:**  The `challenge.model` module encapsulates all data processing, training, and inference logic.  The trained model and OneHotEncoder are saved as artifacts in `challenge/model`.
* **Test Validation:** All tests passed successfully.


<p align="center">
    <img src="https://github.com/user-attachments/assets/2f12a642-1c8a-4906-b001-62e55b375ecb" alt="dashboard"/>
</p>

## Part II: API Development

<p align="center">
    <img src="https://github.com/user-attachments/assets/c7eed62e-1ca0-4382-a2a1-50f935669123" alt="dashboard"/>
</p>

The API design is intended to be clean and robust.


1) Pydantic classes are implemented to validate requests and responses, ensuring data integrity while also providing documentation. 
2) The implementation consists of only four lines of code, keeping it very simple to understand and maintain. All model logic is abstracted into the `DelayModel` class
3) Line 10 allows caching the model across different requests in Cloud Run, enabling the model to load only once and facilitating faster inferences.

<p align="center">
    <img src="https://github.com/user-attachments/assets/b07da720-803e-4207-8ce9-1753ea66629d" alt="dashboard"/>
</p>

#### Usage
**Local API:** The `Dockerfile.dev` builds a development image containing the API, data, and tests for easy local development and debugging.

```bash
docker build -t challenge-dev:v1 . -f Dockerfile.dev
docker run -d --name challenge-dev -p 8081:8080 challenge-dev:v1
```

*This image is used for Continuous Integration.*


**Production API:** The `Dockerfile` builds an optimized production image containing only the necessary files and packages from `requirements.txt`.  This excludes notebooks, test data, and other development-specific files. The API is exposed on port 8080 (the default port for Cloud Run).

```bash
docker build -t challenge:v1 .
docker run -d challenge:v1 -p 8080:8080
```

*This image is used for Continuous Delivery.*


## Part III : Cloud Deployment & Load Tests

In GCP, there are multiple alternatives for deploying REST APIs, such as Cloud Functions, Virtual Machines, App Engine, Cloud Run, and GKE, among others. However, the challenge suggests using GCP, FastAPI, and containers to deploy the API while maintaining high performance.

In this scenario, `Cloud Run` and `GKE` are two excellent candidates that meet these requirements. In this case, `Cloud Run was selected` because it is serverless and allows for greater focus on deployment rather than infrastructure management. However, if more tailored needs arise, GKE could also be considered.

**Cloud Run is configured to meet high demand with low latency times** by setting the minimum instances to 2 and activating CPU boost. However, this configuration may affect billing due to the increased resource usage. If reducing costs is more important than performance, it is better to set the minimum instances to 0 and deactivate CPU boost.

`⚠️: This exposes a public API, for real-world use cases, implementing authentication is highly recommended.`

* **Cloud Run Configuration:**

```bash
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region ${{env.REGION}} \
    --allow-unauthenticated \
    --service-account ${{ secrets.SERVICE_ACCOUNT }} \
    --concurrency 40 \
    --max-instances 30 \
    --min-instances 2 \
    --cpu-boost \
    --execution-environment gen2 \
    --ingress all
```

    * `$SERVICE_NAME`:  The name of your Cloud Run service.
    * `--region`: The GCP region for deployment.
    * `--allow-unauthenticated`: Allows public access to the API.
    * `--service-account`:  Uses a service account for authentication (credentials stored in GitHub Secrets).
    * `--concurrency`:  Sets the maximum concurrent requests per instance.
    * `--min-instances`: Keeps two instances warm to prevent cold starts.
    * `--cpu-boost`: Provides extra CPU during instance startup.

*A service account is used to manage all the authentication, and the credentials are stored under GitHub repository secrets.*


#### Locust: Performance testing

Load testing with Locust demonstrates the API's ability to maintain performance under high load. Based on `make stress-test` the results shows that *regarless the increasing number of users, The API keeps its high performance with median response times below 100ms!*

<p align="center">
    <img src="https://github.com/user-attachments/assets/f2dcc54f-5a8e-481e-86e7-c7e81024ef71" alt="dashboard"/>
</p>

## Part IV : CI/CD

#### **Continuous Integration**

* **Trigger:** Pull request opened or updated against the `main` branch.
* **Purpose:** Validate code quality before merging.
* **Steps:**
  1. Checkout code.
  2. Install Python dependencies (`make install`).
  3. Run API tests (`make api-test`).
  4. Run model tests (`make model-test`).

### Continuous Delivery (CD)

* **Trigger:** Push to the `main` branch.
* **Purpose:** Automatically deploy the latest code to Cloud Run.
* **Steps:**
  1. Checkout code.
  2. Authenticate with GCP (using service account key in GitHub Secrets).
  3. Set up Google Cloud SDK.
  4. Configure Docker for pushing to Google Container Registry (GCR).
  5. Deploy to Cloud Run.

For initial setup the project, you have to run the following commands.

* Enable GCP APIs
```
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com compute.googleapis.com serviceusage.googleapis.com storage.googleapis.com
```
* Create Service Account
```
gcloud iam service-accounts create SERVICE_ACCOUNT_NAME
```
* Give the Service Account Permissions
```
gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com --role=roles/run.admin

gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com --role=roles/cloudbuild.builds.editor

gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com --role=roles/artifactregistry.admin

gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com --role=roles/serviceusage.serviceUsageAdmin

gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com --role=roles/storage.admin

gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com --role=roles/serviceAccountUser
```

* Export the service account keys to GitHub repository secrets with the name `GCP_SA_KEY` to allow GitHub to authenticate and deploy.

## Conclusions

The challenge was fully satisfied by deploying a FastAPI service on GCP using Cloud Run. This solution not only facilitates the deployment of a public API with low latency and high demand handling but also ensures continuous quality validation through Continuous Integration (CI) and continuous updates to the codebase via Continuous Deployment (CD).

In developing this solution, a strong emphasis was placed on clarity and adherence to high-quality code standards, including strict Pydantic validation, type checking, and comprehensive documentation. Furthermore, high-performance strategies were implemented in both the code and infrastructure to ensure efficient resource usage and scalability.

## Future Work.

For future improvements, the following enhancements are suggested:

* **Integrate Pylint in CI**: Add Pylint to the Continuous Integration process to enforce coding standards and improve code quality

* **Implement Infrastructure as Code (IaC):** Utilize a framework such as Terraform to better manage GCP resources and permissions, ensuring a more efficient and organized infrastructure setup.

* **Model Monitoring**: Establish monitoring to identify common issues such as data quality problems, data drift, concept drift, and model performance degradation. This proactive approach will allow for timely interventions and model retraining, ensuring ongoing accuracy and reliability in production
