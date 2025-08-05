
**Google STT home**

https://cloud.google.com/speech-to-text?hl=en

**Transcribe streaming audio from a microphone (python)**

https://cloud.google.com/speech-to-text/docs/samples/speech-transcribe-streaming-mic?hl=en#speech_transcribe_streaming_mic-python

**Endless streaming**

https://cloud.google.com/speech-to-text/docs/transcribe-streaming-audio#endless-streaming

**googletrans**

https://py-googletrans.readthedocs.io/en/latest/

**gcloud init**

https://cloud.google.com/docs/authentication/set-up-adc-local-dev-environment


# https://en.wikipedia.org/wiki/IETF_language_tag#List_of_common_primary_language_subtags
# https://py-googletrans.readthedocs.io/en/latest/#googletrans.models.Translated

# Models
# https://cloud.google.com/speech-to-text/docs/reference/rest/v1/RecognitionConfig

# ONLY for EN
# latest_long : Best for long form content like media or conversation.

# Googletrans

possible languages : https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages

googletrans result is unicode utf-8
https://py-googletrans.readthedocs.io/en/latest/

# Google Speech

possible languages : https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages

speech.result
https://cloud.google.com/speech-to-text/docs/reference/rpc/google.cloud.speech.v1p1beta1#speechrecognitionalternative

# Monitoring

Home : https://console.cloud.google.com
Dashboard : https://console.cloud.google.com/home/dashboard
Metrics : https://console.cloud.google.com/apis/api/speech.googleapis.com/
Billing : https://console.cloud.google.com/billing

# auth

https://cloud.google.com/iam/docs/service-account-creds

	Using a service account key to sign a JSON Web Token (JWT) and exchange it for an access token

https://cloud.google.com/iam/docs/keys-create-delete#required-permissions

	Required roles
	To get the permissions that you need to create and delete service account keys, ask your administrator to grant you the Service Account Key Admin (roles/iam.serviceAccountKeyAdmin) IAM role
	on the project, or the service account whose keys you want to manage. For more information about granting roles, see Manage access to projects, folders, and organizations. 

https://cloud.google.com/iam/docs/service-account-creds#user-managed-keys

	You can create user-managed key pairs for a service account, then use the private key from each key pair to authenticate with Google APIs. This private key is known as a service account key.

- IAM : where the access are managed
- Service Accounts

## logout

	gcloud auth revoke --all
	gcloud auth application-default revoke

## Create key.json

The account needs to have the rights to crete a key

	Service account key creation is disabled
	An Organization Policy that blocks service accounts key creation has been enforced on your organization.
	Enforced Organization Policies IDs: iam.disableServiceAccountKeyCreation

## json local

	Credentials saved to file: [/Users/{user}/.config/gcloud/application_default_credentials.json]

