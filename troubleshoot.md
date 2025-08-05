
# Troubleshoot

**credentials**

	raise exceptions.DefaultCredentialsError(_CLOUD_SDK_MISSING_CREDENTIALS)
	google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found.
	To set up Application Default Credentials

need to auth using gcloud cli

	gcloud auth application-default login

Limitations

	"Exceeded maximum allowed stream duration of 305 seconds."

Installation issues

macos & pyaudio : https://stackoverflow.com/questions/33851379/how-to-install-pyaudio-on-mac-using-python-3
