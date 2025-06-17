import requests
from flask import current_app, request
from pydantic import BaseModel, HttpUrl

import logging

logger = logging.getLogger(__name__)


class AcademicInterest(BaseModel):
    """AcademicInterest is a Pydantic model that represents the academic interest
    data associated with a user.
    """

    id: int
    text: str


class Group(BaseModel):
    """Group model representing a user's group membership."""

    id: int
    group_name: str
    role: str
    url: HttpUrl


class Profile(BaseModel):
    """Profile is a Pydantic model that represents the profile data associated
    with a user.
    """

    username: str
    name: str
    email: str
    first_name: str
    last_name: str
    institutional_affiliation: str
    orcid: str
    academic_interests: list[AcademicInterest]
    groups: list[Group]
    url: HttpUrl | None = None


class SubData(BaseModel):
    """SubData is a Pydantic model that represents the data associated with a
    user profile.
    """

    sub: str
    profile: Profile


class Meta(BaseModel):
    """Meta is a Pydantic model that represents the metadata associated with the
    API response.
    """

    authorized: bool


class APIResponse(BaseModel):
    """APIResponse is a Pydantic model that represents the response from the
    API endpoint.
    """

    data: list[SubData]
    meta: Meta
    next: str | None
    previous: str | None


def fetch_user_profile(sub_id: str) -> APIResponse:
    """Fetch user profile data from the API endpoint.

    Args:
        sub_id: The subject ID to query for

    Returns:
        APIResponse: Parsed response data

    Raises:
        requests.RequestException: If the API request fails
        ValueError: If the bearer token is not found in environment variables
    """
    # Get bearer token from environment variable
    bearer_token = current_app.config.get("STATIC_BEARER_TOKEN")

    if not bearer_token:
        raise ValueError("STATIC_BEARER_TOKEN environment variable not found")

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    # Make the API request
    base_api_url = current_app.config.get("IDMS_BASE_API_URL")
    url = f"{base_api_url}subs/?sub={sub_id}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse JSON response
        json_data = response.json()

        # Parse with Pydantic
        parsed_response = APIResponse(**json_data)

        return parsed_response

    except requests.RequestException:
        message = "API request failed"
        logger.exception(message)
        raise
    except Exception:
        message = "Error parsing response"
        logger.exception(message)
        raise


def update_token_information(
    access_token: str,
    refresh_token: str,
    user_name: str,
    app: str = "Works",
    timeout: int = 30,
) -> requests.Response:
    """Make a POST API request with token data for storage and revocation.

    Args:
        access_token: User's access token
        refresh_token: User's refresh token
        user_name: Username to send
        app: Application name (defaults to "Profiles")
        timeout: Request timeout in seconds

    Returns:
        requests.Response object

    Raises:
        requests.RequestException: If the request fails
    """
    # Get user agent from current request
    user_agent = request.headers.get("User-Agent", "Unknown")

    base_api_url = current_app.config.get("IDMS_BASE_API_URL")
    api_url = f"{base_api_url}tokens/"

    # Get bearer token from environment variable
    bearer_token = current_app.config.get("STATIC_BEARER_TOKEN")

    if not bearer_token:
        raise ValueError("STATIC_BEARER_TOKEN environment variable not found")

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    # Prepare the payload
    payload = {
        "user_agent": user_agent,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "app": app,
        "user_name": user_name,
    }

    # Make the POST request
    response = requests.post(
        api_url, json=payload, headers=headers, timeout=timeout
    )

    # Raise an exception if the request fails
    response.raise_for_status()

    return response
