import os
from urllib.parse import urlencode
import requests

def get_authorize_url(state: str = None) -> str:
    """
    Build the URL to redirect users to Globus Auth’s /authorize.
    """
    auth_url    = os.getenv("GLOBUS_AUTH_URL")       # e.g. https://auth.globus.org/v2/oauth2/authorize
    client_id   = os.getenv("GLOBUS_CLIENT_ID")    
    redirect_to = os.getenv("GLOBUS_REDIRECT_URI")   # http://localhost:5000/globus/callback
    scope       = os.getenv("GLOBUS_SCOPE")          # urn:globus:auth:scope:transfer.api.globus.org:all

    # Build the query‐string parameters
    params = {
        "client_id":     client_id,
        "redirect_uri":  redirect_to,
        "response_type": "code",    # standard OAuth2 authorization‐code grant
        "scope":         scope,
    }
    if state:
        params["state"] = state

    # Return the full URL:
    #    https://auth.globus.org/v2/oauth2/authorize?client_id=…&redirect_uri=…
    return f"{auth_url}?{urlencode(params)}"


def exchange_authorization_code(code: str) -> dict:
    """
    Given the `code` from callback, POST to Globus Auth’s /token endpoint
    and return the JSON payload `{access_token, expires_in, …}`.
    """
    token_url     = os.getenv("GLOBUS_TOKEN_URL")      # e.g. https://auth.globus.org/v2/oauth2/token
    client_id     = os.getenv("GLOBUS_CLIENT_ID")     # from .env
    client_secret = os.getenv("GLOBUS_CLIENT_SECRET") # from .env
    redirect_to   = os.getenv("GLOBUS_REDIRECT_URI")  # must match exactly what we sent

    # The form‐data to send
    payload = {
        "grant_type":   "authorization_code",
        "code":         code,
        "redirect_uri": redirect_to,
    }

    # requests will automatically do HTTP Basic for us:
    resp = requests.post(
        token_url,
        data=payload,
        auth=(client_id, client_secret),
    )
    resp.raise_for_status()   # blow up if we got a 4xx/5xx
    return resp.json()        # { access_token: "...", expires_in: ..., ... }
