# Bictoin Stock Price Forecasting
Deployment of a Bitcoin forecasting pipeline on AWS services.

In this repository, we create a forecasting pipeline deployable through 3 different AWS services :
- Amazon SageMaker
- Amazon Lambda
- Amazon API Gateway

The final goal is to be able to predict next week stock price based on stock historical data (daily).

# Instructions to launch the SageMaker Instance

1. Log in AWS
2. Select **SageMaker** in **Services**
3. Go to **Notebook** section and click on **Create a notebook instance**
4. Choose a name. for example *btc-prediction-aws* for this particular project
5. In **Git Repositories** section, choose **Clone a public Git repository to this notebook instance only** and enter the Git repo URL: *https://github.com/emilecohen/btc_prediction_aws.git*

Afterwards, you will have to wait a few minutes for your instance to be InService.

When opening the Notebook for the first time, choose the Kernel **conda_mxnet_p36**


# Instructions to instantiate the containers and create the forecasting model

 You will find all useful information in the Notebook:
 - CryptoCompare API Call
 - Discovery of the Data
 - Creation of the model
 - Training and Testing of the model
 - Creation of a model endpoint for the deployment
 - Instructions to create Lambda function and API Gateway
