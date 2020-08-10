# RemindBot

_An SMS-based reminder chatbot Nexmo, Google Calendars & Gmail, and IBM Watson._

August 25, 2017

When our lives become filled with activity, organization is key. Sometimes there is too much going on to remember, so we must reply on a system to remind ourselves of deadlines, tasks, or events. There are countless applications available for download that set reminders, but these apps demand storage space, take time to set up, and can be inconvenient and frustrating to use. If you want to create a calendar event, you're forced to download an app and use a cluttered interface. What if we could send ourselves reminders or create future events simply by sending a text?

With IBM Watson, Google Calendars, and Gmail, we can build a Nexmo-powered chatbot. The bot works by interpreting our requests to set reminders with Watson and extracting the date, time, and title of the reminder. The chatbot stores your reminder by creating an event in your personal Google Calendar and notifies you via SMS and email when the event occurs. 

The program will be stored on AWS Lambda and linked to API Gateway.

## [Demo](https://drive.google.com/file/d/12XMIs-Q0SW7KFSLqqF9iB26mXQ3AW_Vj/view?usp=sharing)

## Prerequisites

-  Python 2.7
- [Nexmo](https://nexmo.com/sign-up)
- [IBM Watson](https://www.ibm.com/watson/)
- [Google Calendar & Gmail](https://accounts.google.com/SignUp)
- [AWS Lambda, API Gateway, RDS DB Instance](https://aws.amazon.com/free/)

## Installation

#### 1. Clone the Remind-Bot Github repository

`cd /path/to/your_repository`

`git clone https://github.com/kasey-mcfadden/RemindBot`

Cloning the repository will create a folder on your local machine containing all the necessary files for this project.

___

#### 2. Install Requirements

`pip install -t /path/to/your_repository -r requirements.txt`

This step is needed to store all the required python packages in the repository you have cloned. This way, AWS Lambda will be able to import the packages when we upload the compressed files to our Lambda function.

___

#### 3. Create the AWS Lambda function

AWS Lamba is where our program will be stored, and is essentially the center of our chatbot. This is where the HTTP requests sent by Nexmo, Watson, and Google are interpreted. It also controls how we will manage the RDS database, send event information to the user's calendar, and deliver SMS messages to the user.

Create a new [Lambda function](https://console.aws.amazon.com/lambda#/create/) > Author from scratch

_Basic information_

Name: **Remind-Bot**

Runtime: **Python 2.7**

_Lambda function code_

Code entry type > **Upload a .ZIP file**

Upload > Compress and upload this cloned repository: **remind-bot.zip**

_Lambda function handler and role_

Handler: **_interact.lambda_handler_**

Role > Choose an existing role: **IPA-Lambda**

_Advanced settings_

Memory: **128 MB**

Timeout: **6 sec**

___

#### 4. Create API in API Gateway

For HTTP requests to be delivered to our Lambda function, we need to establish webhook endpoints. With API Gateway, we can define what happens when these endpoints are called by linking them to our Lambda function.

Before we import our API from the swagger file in GitHub, we must customize it to match our AWS host.

Edit swagger file: open **Remind-Bot-API-GW-swagger.json** > specify your AWS host (**"host", line 7**)

Now, we can create the [API](https://console.aws.amazon.com/apigateway#/apis/create)

Import from Swagger > Select Swagger File: **Remind-Bot-API-GW-swagger.json**

> Import 

Set up methods for **/auth**, **/auth/code**, **/interact**, and **/notifications**:

Integration type: **Lambda Function**

- [x] Use Lambda Proxy integration

Lambda Region: same region as Lambda Function

Lambda Function: **Remind-Bot** 

> Save

![alt text](https://github.com/kasey-mcfadden/RemindBot/blob/master/API-GW.png?raw=true "API Gateway Interface")

Select Actions > Deploy API > **Deploy**

In the Stage Editor interface, take note of the **Invoke URL**. This is the base URL that Nexmo, Watson, and Google will use to call our endpoints.

___

#### 5. Create RDS Database

Use the commands in the `remindbot.ddl` file to create a new database with a table titled 'phone_numbers'.

Your 'phone_numbers' database will have two columns; the first will store users' phone numbers and the second will store their google credentials in a base64-encoded format.

The database will look something like this once users have registered for Remind-Bot:

|      id       |  credentials  |
| ------------- |---------------|
| 12345678999   | google-creds  |
| 19876543210   | sample-creds  |

___

#### 6. Integrate Nexmo

Once you've registered for an Nexmo account and have received a virtual number, [edit your number](https://dashboard.nexmo.com/your-numbers).

It's time to specify where we want SMS messages received by Nexmo to be sent. Now that **Invoke URL** we received in Step 4 will come in handy.

Specify the Webhook URL for your virtual number: **https:// INVOKE-URL /interact**

Ignore the voice options - these do not matter for our project because it is strictly SMS-based.

![alt text](https://github.com/kasey-mcfadden/RemindBot/blob/master/Nexmo-Dash.png?raw=true "Nexmo Dashboard")

Now, whenever your virtual number receives an SMS message, it will invoke the Lambda function with the message data by calling this Webhook URL!

___

#### 7. Integrate IBM Watson

Create a new [Watson Conversation Workspace](https://watson-conversation.ng.bluemix.net) by importing a workspace.

Choose **watson_workspace.json** and select Import Everything (Intents, Entities, and Dialog).

View the details of your imported workspace and take note of the **Workspace ID**.

Grab your Watson Conversation [Service Credentials](https://www.ibm.com/watson/developercloud/doc/common/getting-started-credentials.html) and keep track of these values.

___

#### 8. Create Google project and enable push notifications

Start a [Google API Console project](https://developers.google.com/identity/sign-in/web/devconsole-project)

Enable the [Calendar API and Gmail API](https://console.developers.google.com/apis/library) for your project

Create an Oauth client ID for Application type > **Web application**

Name the application **Remind-Bot**. Under Authorized redirect URIs, enter **https:// INVOKE-URL /auth/code** and **https://localhost:8080**.

Download the JSON file of your Web Client ID as **_client_secrets.json_**

Add a Property to your API Gateway Invoke URL in the [Google Search Console](https://www.google.com/webmasters/tools/home)

Download the user-specific HTML verification file [YOUR-GOOGLE-HTML-VERIFICATION.html] and save it as _google_validation_file.html_

In the Lambda management console, set _google_file_name_ as an environment variable with a value of YOUR-GOOGLE-HTML-VERIFICATION.html

Navigate to your [API Gateway Project](https://console.aws.amazon.com/apigateway#/apis)

Actions > **Create resource**

Configure as proxy resource: No

Resource Name: **YOUR-GOOGLE-HTML-VERIFICATION.html**

Resource Path: **/YOUR-GOOGLE-HTML-VERIFICATION.html**

> Create Resource

Create a **GET** method for the HTML verification resource that integrates with the **Remind-Bot** Lambda function.

Return to the Google Search Console and verify the Invoke URL.

Verify your API Gateway Invoke URL for your Google API Console project with [Google Domain Verification](https://console.developers.google.com/apis/credentials/domainverification)

In the [Google Cloud Platform](https://console.cloud.google.com/cloudpubsub/), create a topic and subscription. For the subscription delivery type, select **Push into an endpoint URL** and enter **https:// INVOKE-URL /notifications** as the endpoint URL that will receive POST requests.

Under topic permissions, add **gmail-api-push@system.gserviceaccount.com** as a _Pub/Sub Publisher_.

___

#### 9. Create default google credentials

Create a [new google account](https://accounts.google.com/SignUp). This will be your master account for this project.

Create your default credentials for the master account:

`cd /path/to/your_repository`

`python creds_test.py`

You'll be redirected to a window in your browser and prompted to log in to google. Sign in with your master account. Once the authentication flow completes, you should have a file in _default_credentials.json_ file in /path/to/your_repository.

___

#### 10. Finalize things in AWS Lambda

Compress your repository. Re-upload the .zip file to Lambda.

In your [Lambda function](https://console.aws.amazon.com/lambda) console, specify the following environment variables:
- _watson_user_ = username from Watson Conversation service credentials
- _watson_pass_ = password from Watson Conversation service credentials
- _watson_workspace_ = IBM Watson Workspace ID
- _redirect_uri_ = https:// INVOKE-URL /auth/code
- _db_host_ = RDS Database host
- _db_name_ = RDS Database name
- _db_user_ = RDS Database authorized user
- _db_pass_ = RDS Database password
- _nexmo_number_ = your virtual number provided by Nexmo
- _nexmo_api_key_ = your key from the API credentials located on [Nexmo's dashboard](https://dashboard.nexmo.com/getting-started-guide)
- _nexmo_api_secret_ = your secret from the Nexmo API credentials
- _google_file_name_ = YOUR-GOOGLE-HTML-VERIFICATION.html
- _master_email_ = master email address

![alt text](https://github.com/kasey-mcfadden/RemindBot/blob/master/env-vars.png?raw=true "Lambda Environment Variables")

> Save

Test out the Remind-Bot! Send a text to your virtual Nexmo number to get started.

## Credits

*A project by [Kasey McFadden](https://www.linkedin.com/in/kasey-m-414565103), overseen by [Murali Ramsunder](https://www.linkedin.com/in/murali-ramsunder-5025856/)*

## License

MIT
