<p align="center">
  <i align="center">Software Engineer (ML & LLMs) Challenge
  - Solution by Alejandro Aponte🚀</i>
</p>


<p align="center">
    <img src="https://github.com/user-attachments/assets/9e9a155b-6cf4-4604-974c-4657eaf0265c" alt="dashboard"/>
</p>


## Introduction

# Flight Delay Prediction API - Solution

This document details the solution for deploying a high-performance machine learning model on Google Cloud Platform (GCP) via a REST API. This API predicts the probability of flight delays for arrivals and departures at SCL airport.


#### Key Features

* **Fast:**  Median API response time is consistently below 100ms. (See Locust Report below)
* **Robust:**  Pydantic validation ensures data quality and prevents unexpected errors.
* **Scalable:** Cloud Run automatically scales to handle fluctuating traffic demands.
* **Cost-Effective:** Serverless architecture means you only pay for resources consumed. Minimum instances are configured to balance cost and responsiveness.
* **CI/CD Integrated:** Automated build, test, and deployment pipelines streamline the development process.
* **Optimized:** A slim Docker image (python:3.9-slim-bullseye) minimizes deployment size and improves startup time.  Efficient Docker build caching further speeds up the process.
* **Well-Documented:** Clear and comprehensive documentation facilitates understanding and maintenance.

#### Stack
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

## Part I: Model Development

* **Package Management:** Resolved package incompatibilities and added missing packages (e.g., XGBoost) to `requirements.txt`.  New packages were chosen to maintain compatibility with existing ones.
* **Model Selection:** Evaluated Logistic Regression and XGBoost with feature importance and balanced data.  Logistic Regression was selected for its simplicity, smaller footprint, and comparable performance.
* **Model Training/Inference:**  The `challenge.model` module encapsulates all data processing, training, and inference logic.  The trained model and OneHotEncoder are saved as artifacts in `challenge/model`.
* **Test Validation:** All tests passed successfully.


<p align="center">
    <img src="https://github.com/user-attachments/assets/2f12a642-1c8a-4906-b001-62e55b375ecb" alt="dashboard"/>
</p>

## Part II: API Development

<p align="center">
    <img src="https://github.com/user-attachments/assets/b07da720-803e-4207-8ce9-1753ea66629d" alt="dashboard"/>
</p>


**Local API:** The `Dockerfile.dev` builds a development image containing the API, data, and tests for easy local development and debugging.

```bash
docker build -t challenge-dev:v1 . -f Dockerfile.dev
docker run -d --name challenge-dev -p 8081:8080 challenge-dev:v1
```

* **Production API:** The `Dockerfile` builds an optimized production image containing only the necessary files and packages from `requirements.txt`.  This excludes notebooks, test data, and other development-specific files. The API is exposed on port 8080 (the default port for Cloud Run).

```bash
docker build -t challenge:v1 .
docker run -d challenge:v1 -p 8080:8080
```

This image is used for Continuous Delivery.


## Part III : GCP Infrastructure & Locust


* **GCP Cloud Run:** Cloud Run was chosen for its serverless nature, container support, and automatic scaling capabilities.  It avoids the overhead of managing a Kubernetes cluster.

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

* A service account has use to manage all the authentication, the credentials lies under Github Repository secrets.


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

