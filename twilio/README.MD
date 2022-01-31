### Getting Started with Twilio Functions

- **Create the Twilio Function Service**: If there has not been a function service created, on the Twilio Console click Functions/Services, then Create Service. Enter a service name.
- **Add the BigQuery Node.js Client**: Click on Settings/Dependencies. Add the module '@google-cloud/bigquery', version 5.10.0 as of this writing. Check [NPM](https://www.npmjs.com/package/@google-cloud/bigquery) for more recent versions.
- **Add a Service Account to GCP with BigQuery access permissions**: Go to your Google Cloud Console, then IAM & Admin/Service Accounts, and create a new service account with sufficient permissions (i.e., BigQuery Data Viewer and BigQuery Job User). If you already have a service account and need to add permissions, go to IAM & Admin/IAM, then find the service account you would like to edit.
- **Create BigQuery Key**: Go to your Google Cloud Console, then IAM & Admin/Service Accounts, and click on the service account you just created. Click on KEYS. Click on "ADD KEY" then "Create new key". Select json key type, then CREATE. The json will automatically download to your computer.
- **Add BigQuery the BigQuery Key to Twilio Functions**: On your Twilio Function Service page, click on "Add +", then "Add Asset (static text file)". Create an asset named "gcp_service_account.json". In the editor delete any sample text and paste in the JSON text that you just downloaded from Google Cloud Console. Change the mode of the asset from "Protected" to "Private". Click "Save". The text should look something like the following:

```
{
  "type": "service_account",
  "project_id": "courtbot",
  "private_key_id": "SECRETSECRET",
  "private_key": "-----BEGIN PRIVATE KEY-----\nSECRETSECRET\n-----END PRIVATE KEY-----\n",
  "client_email": "google-service-account@courtbot.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-service-account%40courtbot.iam.gserviceaccount.com"
}
```

- **Create the Twilio Function**: On your Twilio Function Service page, click on "Add +", then "Add Function". Give it a path name, e.g., '/bigquery'. Delete any existing sample code and paste in the twilio_functions.js code from this folder. Review the sqlQuery strings and adjust the queries as needed for your data. Select "Save" then "Deploy All"
- **Run the Function from Twilio Studio**: The function may be run in two modes from Twilio Studio. In the first mode the parameter is the text string "user_text". The function uses RegEx to attempt to extract a case number, then runs an SQL query to check if the case number exists in the db. It returns a boolean case_found, indicating whether a case number was extracted from the text and found in the db. If so, it also returns a case_number string. If not it returns an error_msg string. In the second mode the parameter is the text string "case_number". The function queries the database and returns the following: hearing_found (boolean), date (string), time (string), coutroom (string).
