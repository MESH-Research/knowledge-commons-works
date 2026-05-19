# Outgoing Signals

KCWorks sends signals to other Knowledge Commons services in certain situations.

```{warning}
These endpoints are part of the internal Knowledge Commons integration. They are documented for operators and developers integrating with KCWorks, not for general API consumers.
```

## Logout signal (to Profiles / IDMS)

When a user logs out of KCWorks, KCWorks notifies the central Knowledge Commons identity/profiles service so that the user can be logged out across other applications in the network (single sign-out).

### When it is sent

The signal is sent when the user completes logout in KCWorks (e.g. by clicking logout in the UI). It is triggered by the `user_logged_out` signal (from `flask_login`), which triggers a handler that subscribes to the signal in `kcworks.ext`.

### Destination

- **URL**: `{IDMS_BASE_API_URL}actions/logout/`  
  The base URL is set by the `IDMS_BASE_API_URL` configuration variable.
- **Method**: `POST`
- **Authentication**: Bearer token. The token is read from the environment variable `COMMONS_PROFILES_API_TOKEN`.

### Request headers

| Header          | Value                                 |
| --------------- | ------------------------------------- |
| `Authorization` | `Bearer <COMMONS_PROFILES_API_TOKEN>` |
| `Content-Type`  | `application/json`                    |
| `Accept`        | `application/json`                    |

### Request body

JSON object:

| Property     | Type   | Description                                                                 |
| ------------ | ------ | --------------------------------------------------------------------------- |
| `user_name`  | string | The Knowledge Commons username of the user who logged out.                  |
| `user_agent` | string | The `User-Agent` header from the HTTP request in which the user logged out. |

Example:

```json
{
  "user_name": "john_doe",
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ..."
}
```

```{note}
The username provided in this signal is *not* necessarily the same as the KCWorks user account's username. It is the user's username in the broder Knowledge Commons network. We are migrating towards harmonized usernames accross apps, but for the moment this harmonization is incomplete. The central KC username is available under the `identifier_kc_username` key of the user's profile (`User.user_profile`).

Note that this is also *not* the same as the user's `cilogon` subject id, which is used for authentication and linked to the KCWorks user in the `UserIdentity` model.
```

### Expected success response

The Profiles API is expected to return HTTP 200 with a JSON body similar to:

```json
{
  "message": "Action successfully triggered.",
  "data": {
    "user": {
      "user": "john_doe",
      "url": "/profiles/john_doe/"
    },
    "user_agent": "Mozilla/5.0 ...",
    "app": ["Profiles", "Works", "WordPress"]
  }
}
```

KCWorks treats the request as successful when the status code is in the 2xx range and the response body contains the expected structure (including `data.user.user` matching the sent `user_name`).

### Error handling

KCWorks does not raise an error to the user if the outgoing logout request fails. The result is logged and the function returns `False`; the user's KCWorks logout still completes. Failures can include:

- **HTTP 400** — Validation error (e.g. empty `user_name` or `user_agent`).
- **HTTP 401** — Missing or invalid Bearer token.
- **HTTP 500** — Server error from the Profiles API.
- **Network/timeout errors** — Connection failures or timeout (default 15 seconds).
