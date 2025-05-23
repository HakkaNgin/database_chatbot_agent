from msal import ConfidentialClientApplication

app = ConfidentialClientApplication(
    client_id='CLIENT_ID',
    client_credential='CLIENT_SECRET',
    authority='https://login.microsoftonline.com/TENANT_ID'
)

token_response = app.acquire_token_for_client(scopes=['https://analysis.windows.net/powerbi/api/.default'])
access_token = token_response['access_token']
