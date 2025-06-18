"""Utility functions for CILogon integration."""

import base64
import datetime
import hashlib
import json
import os
from urllib.parse import urlencode, urlunparse, urlparse

import invenio_oauthclient
import jwt
import requests
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import current_app, abort
from invenio_accounts import current_accounts
from invenio_accounts.models import User, UserIdentity
from invenio_db import db
from jwt.algorithms import RSAAlgorithm

from kcworks.services.cilogon.api import update_token_information
from kcworks.services.cilogon.groups import GroupRolesComponent


class SecureParamEncoder:
    """Encrypt and encode data for URL transmission."""

    def __init__(self, shared_secret: str):
        """Initialize the SecureParamEncoder.

        Args:
            shared_secret (str): The shared secret used for encryption.
        """
        # Derive a 32-byte key from any length secret
        self.key = hashlib.sha256(shared_secret.encode()).digest()

    def encode(self, data: dict) -> str:
        """Encrypt and encode data."""
        json_data = json.dumps(data).encode()

        # Generate random IV (init vector)
        iv = os.urandom(16)

        # Pad data to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(json_data) + padder.finalize()

        # Encrypt
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()

        # Combine IV + encrypted data
        result = iv + encrypted
        return base64.urlsafe_b64encode(result).decode()

    def decode(self, encrypted_param: str) -> dict:
        """Decrypt and decode data."""
        data = base64.urlsafe_b64decode(encrypted_param.encode())

        # Extract IV and encrypted data
        iv = data[:16]
        encrypted = data[16:]

        # Decrypt
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted) + decryptor.finalize()

        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        json_data = unpadder.update(padded_data) + unpadder.finalize()

        return json.loads(json_data.decode())


class CILogonHelpers:
    """CILogon helper functions."""

    @staticmethod
    def _diff_between_nested_dicts(original, update):
        """Return the difference between two nested dictionaries.

        At present doesn't distinguish between additions and removals
        from lists
        """  # noqa
        diff = {}
        if not original:
            return update
        else:
            for key, value in update.items():
                if isinstance(value, dict):
                    diff[key] = CILogonHelpers._diff_between_nested_dicts(
                        original.get(key, {}), value
                    )
                elif isinstance(value, list):
                    diff[key] = [
                        i for i in value if i not in original.get(key, [])
                    ] + [x for x in original.get(key, []) if x not in value]
                else:
                    if original.get(key) != value:
                        diff[key] = value
            diff = {k: v for k, v in diff.items() if v}
            return diff

    @staticmethod
    def _get_cilogon_public_key(kid):
        """Fetch the specific public key from CILogon's JWKS endpoint."""
        jwks_url = "https://cilogon.org/oauth2/certs"

        try:
            response = requests.get(jwks_url)
            response.raise_for_status()
            jwks = response.json()

            # Find the key with matching kid (Key ID)
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    # Convert JWK to PEM format
                    public_key = RSAAlgorithm.from_jwk(key)
                    return public_key

            raise ValueError(f"Key with kid '{kid}' not found in JWKS")

        except requests.RequestException as e:
            message = "Failed to fetch JWKS"
            raise ValueError(message) from e

    @staticmethod
    def _verify_and_decode_cilogon_jwt(id_token, client_id):
        """Verify and decode a CILogon JWT token."""
        try:
            # Get the key ID from the JWT header (without verification)
            unverified_header = jwt.get_unverified_header(id_token)
            kid = unverified_header["kid"]

            # Fetch the corresponding public key
            public_key = CILogonHelpers._get_cilogon_public_key(kid)

            # Decode and verify the JWT
            decoded_token = jwt.decode(
                id_token,
                public_key,
                algorithms=["RS256"],
                audience=f"cilogon:/client_id/{client_id}",
                issuer="https://cilogon.org",
                options={
                    "verify_exp": True,  # Verify expiration
                    "verify_aud": False,  # Verify audience
                    "verify_iss": True,  # Verify issuer
                },
            )

            return decoded_token

        except jwt.ExpiredSignatureError as e:
            raise ValueError("Token has expired") from e
        except jwt.InvalidAudienceError as e:
            raise ValueError("Invalid audience") from e
        except jwt.InvalidIssuerError as e:
            raise ValueError("Invalid issuer") from e
        except jwt.InvalidTokenError as e:
            message = "Invalid token"
            raise ValueError(message) from e

    @staticmethod
    def build_association_url(id_token):
        """Build the association URL."""
        base_url = current_app.config.get("IDMS_BASE_ASSOCIATION_URL")
        params = {"userinfo": id_token}

        # encode the query string
        encoder = SecureParamEncoder(
            current_app.config.get("STATIC_BEARER_TOKEN")
        )

        encoded_params = {"userinfo": encoder.encode(params)}
        query_string = urlencode(encoded_params)
        parsed_url = urlparse(base_url)

        # Reconstruct the URL
        return urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                query_string,
                parsed_url.fragment,
            )
        )

    @staticmethod
    def _get_external_id(account_info):
        """Get external id from account info."""
        if all(k in account_info for k in ("external_id", "external_method")):
            return dict(
                id=account_info["external_id"],
                method=account_info["external_method"],
            )
        return None

    @staticmethod
    def get_user_from_account_info(
        account_info: dict | None = None,
    ) -> User | None:
        """Retrieve user object for the given request.

        Extends invenio_saml.invenio_accounts.utils.account_get_user to allow for
        retrieving a user by ORCID as well as email.

        Uses either the access token or extracted account information to retrieve
        the user object.

        Parameters:
            account_info (dict | None): The dictionary with the account info.
                (Default: ``None``)

        Returns:
            A :class:`invenio_accounts.models.User` instance or ``None``.
        """
        if not account_info:
            return None

        # Try external ID first
        user = CILogonHelpers._try_get_user_by_external_id(account_info)
        if user:
            current_app.logger.debug("User found by external ID (CILogon)")
            return user

        # Extract user profile safely
        user_profile = account_info.get("user", {}).get("profile", {})

        # Try ORCID lookup
        user = CILogonHelpers._try_get_user_by_orcid(
            user_profile.get("identifier_orcid")
        )
        if user:
            current_app.logger.debug("User found by ORCID")
            return user

        # Try KC username lookup
        user = CILogonHelpers._try_get_user_by_kc_username(
            user_profile.get("identifier_kc_username"),
            account_info.get("external_method"),
        )
        if user:
            current_app.logger.debug("User found by KC username")
            return user

        # Try email lookup
        email = account_info.get("user", {}).get("email")
        user = CILogonHelpers._try_get_user_by_email(email)
        if user:
            current_app.logger.debug("User found by email")
            return user

        return None

    @staticmethod
    def _try_get_user_by_external_id(account_info: dict) -> User | None:
        """Try to get user by external ID."""
        try:
            external_id = CILogonHelpers._get_external_id(account_info)
            if external_id:
                return UserIdentity.get_user(
                    external_id["method"], external_id["id"]
                )
        except Exception:
            # Log the exception in a real implementation
            pass
        return None

    @staticmethod
    def _try_get_user_by_orcid(orcid: str | None) -> User | None:
        """Try to get user by ORCID."""
        if not orcid:
            return None

        try:
            return User.query.filter(
                User._user_profile.op("->>")("identifier_orcid") == orcid
            ).one_or_none()
        except Exception:
            pass
        return None

    @staticmethod
    def _try_get_user_by_kc_username(
        kc_username: str | None, external_method: str | None
    ) -> User | None:
        """Try to get user by KC username."""
        if not kc_username:
            return None

        # check if the username is a direct valid kc identifier
        user = User.query.filter_by(username=f"{kc_username}").one_or_none()
        if user:
            return user

        try:
            # First try with external method prefix
            if external_method:
                user = User.query.filter_by(
                    username=f"{external_method}-{kc_username}"
                ).one_or_none()
                if user:
                    return user

            # Then try profile lookup
            return User.query.filter(
                User._user_profile.op("->>")("identifier_kc_username")
                == kc_username
            ).one_or_none()
        except Exception:
            pass
        return None

    @staticmethod
    def _try_get_user_by_email(email: str | None) -> User | None:
        """Try to get user by email."""
        if not email:
            return None

        try:
            return User.query.filter_by(email=email).one_or_none()
        except Exception:
            pass
        return None

    @staticmethod
    def link_user_to_oauth_identifier(
        user: User, external_method: str, external_id: str
    ) -> None:
        """Ensure that a user has a linked identity with the  external ID."""
        existing_identity = UserIdentity.query.filter_by(
            method=external_method, id=external_id
        ).first()

        if existing_identity:
            current_app.logger.debug(
                "User already has identity linked to CILogon"
            )
            # Update existing record if needed
            if existing_identity.user != user:
                existing_identity.user = user
                db.session.commit()
            _ = existing_identity
        else:
            current_app.logger.debug("Creating new identity for CILogon")
            # Create new UserIdentity
            _ = UserIdentity.create(
                user=user, method=external_method, external_id=external_id
            )
            db.session.commit()

    @staticmethod
    def _update_invenio_group_memberships(
        user: User, changed_memberships: dict, **kwargs
    ) -> list[str]:
        """Update the user's group role memberships.

        If an added group role does not exist, it will be created. If a
        dropped group role does not exist, it will be ignored. If a
        dropped group role is left with no members, it will be deleted
        from the system roles.

        Returns:
            list: The updated list of group role names.
        """
        grouper = GroupRolesComponent(None)
        updated_local_groups = [r.name for r in user.roles]

        for group_name in changed_memberships["added_groups"]:
            group_role = grouper.find_or_create_group(group_name)
            if (
                group_role
                and grouper.add_user_to_group(group_role, user) is not None
            ):
                updated_local_groups.append(group_role.name)

        for group_name in changed_memberships["dropped_groups"]:
            group_role = grouper.find_group(group_name)

            if (
                group_role
                and grouper.remove_user_from_group(group_role, user)
                is not None
            ):
                updated_local_groups.remove(group_role.name)
                # NOTE: We don't delete the group role because that would
                # potentially disrupt roles being used for collections
        assert updated_local_groups == [r.name for r in user.roles]

        return updated_local_groups

    @staticmethod
    def update_local_user_data(
        user: User,
        new_data: dict,
        user_changes: dict,
        group_changes: dict,
        **kwargs,
    ) -> dict:
        """Update Invenio user data for the supplied identity.

        Parameters:
            user (User): The user to be updated.
            new_data (dict): The new user data.
            user_changes (dict): The changes to the user data.
            group_changes (dict): The changes to the user's group memberships.

        Returns:
            dict: A dictionary of the updated user data with the keys "user"
                  and "groups".
        """
        updated_data = {}
        if user_changes:
            # if email changes, keep teh old email as an
            # `identifier_email` in the user_profile
            user.username = new_data["username"]
            user.user_profile = new_data["user_profile"]
            user.preferences = new_data["preferences"]
            if user.email != new_data["email"]:
                user.user_profile["identifier_email"] = user.email
            user.email = new_data["email"]
            current_accounts.datastore.commit()
            updated_data["user"] = user_changes
        else:
            updated_data["user"] = []
        if group_changes.get("added_groups") or group_changes.get(
            "dropped_groups"
        ):
            updated_data["groups"] = (
                CILogonHelpers._update_invenio_group_memberships(
                    user, group_changes, **kwargs
                )
            )
        else:
            updated_data["groups"] = group_changes["unchanged_groups"] or []

        return updated_data

    @staticmethod
    def calculate_user_changes(result, user):
        """Calculate the changes between the existing user and remote data."""
        initial_user_data = {
            "username": user.username,
            "preferences": user.preferences,
            "roles": user.roles,
            "email": user.email,
            "active": user.active,
        }

        try:
            initial_user_data["user_profile"] = user.user_profile
            current_app.logger.debug(
                f"Initial user profile: {user.user_profile}"
            )
        except ValueError:
            current_app.logger.error(
                f"Error fetching initial user profile data for user {user.id}. "
                f"Some data in db was invalid. Starting fresh with incoming "
                "data."
            )
            initial_user_data["user_profile"] = {}

        users = result.data[0].profile

        new_data: dict = {"active": True}
        new_data["user_profile"] = {**initial_user_data["user_profile"]}
        new_data["user_profile"].update(
            {
                "full_name": users.name,
                "name_parts": json.dumps(
                    {
                        "first": users.first_name,
                        "last": users.last_name,
                    }
                ),
            }
        )
        if users.institutional_affiliation:
            new_data["user_profile"][
                "affiliations"
            ] = users.institutional_affiliation
        if users.orcid and users.orcid != "":
            new_data["user_profile"]["identifier_orcid"] = users.orcid
        new_data["user_profile"]["identifier_kc_username"] = users.username
        new_data["username"] = users.username
        new_data["email"] = users.email
        new_data["preferences"] = user.preferences
        new_data["preferences"].update(
            {
                "visibility": "public",
                "email_visibility": "public",
            }
        )
        user_changes = CILogonHelpers._diff_between_nested_dicts(
            initial_user_data, new_data
        )
        return user_changes, new_data

    @staticmethod
    def calculate_group_changes(result, user):
        """Calculate the changes between the existing user and the data."""
        local_groups = [r.name for r in user.roles]
        group_changes = {
            "dropped_groups": [],
            "added_groups": [],
            "unchanged_groups": local_groups,
        }
        users = result.data[0].profile
        if users:
            groups = users.groups
            if groups:
                remote_groups = []
                groups = [g for g in groups if g.group_name]
                for g in groups:
                    # Fetch group metadata from remote service
                    # slug = make_base_group_slug(g["name"])
                    role_string = f"knowledgeCommons---{g.id}|{g.role}"
                    remote_groups.append(role_string)

                if remote_groups != local_groups:
                    group_changes = {
                        "dropped_groups": [
                            g
                            for g in local_groups
                            if g.split("---")[0] == "knowledgeCommons"
                            and g not in remote_groups
                        ],
                        "added_groups": [
                            g for g in remote_groups if g not in local_groups
                        ],
                    }

                    group_changes["unchanged_groups"] = [
                        r
                        for r in local_groups
                        if r not in group_changes["dropped_groups"]
                    ]
        return group_changes

    @staticmethod
    def validate_token_and_extract_sub(resp):
        """Validate token and extract the sub field from the CILogon response."""
        if not resp or "id_token" not in resp:
            raise abort(403)
        id_token = resp.get("id_token")

        try:
            decoded_token = CILogonHelpers._verify_and_decode_cilogon_jwt(
                id_token, os.getenv("CILOGON_CLIENT_ID")
            )
        except ValueError as ve:
            raise abort(403) from ve

        if not decoded_token or "sub" not in decoded_token:
            raise abort(403)

        sub = decoded_token.get("sub")
        return decoded_token, id_token, sub

    @staticmethod
    def update_token_data(resp, result):
        """Update token data in the remote IDMS API.

        The reason we do this is to ensure that the tokens are up to date
        so that when the user does a logout, they can be logged out of
        all services (Single Sign Out).
        """
        try:
            update_token_information(
                resp.get("access_token"),
                resp.get("refresh_token"),
                result.data[0].profile.username,
                timeout=30,
            )
        except Exception:  # noqa: BLE001
            # semi-silently fail if we can't update the token
            current_app.logger.error(
                "Failed to update token information in central API"
            )

    @staticmethod
    def build_account_info(result, sub):
        """Build an account_info dict that looks as expected."""
        account_info = {
            "user": {
                "profile": {
                    "identifier_orcid": result.data[0].profile.orcid,
                    "identifier_kc_username": result.data[0].profile.username,
                }
            },
            "external_id": sub,
            "external_method": "cilogon",  # or "orcid"
        }
        return account_info

    @staticmethod
    def create_new_user(result):
        """Create a new user."""
        current_app.logger.debug(
            f"Creating user: {result.data[0].profile.username}"
        )
        user_info = {
            "username": result.data[0].profile.username,
            "email": result.data[0].profile.email,
            "active": True,
            "confirmed_at": (datetime.datetime.now(datetime.UTC)),
        }
        user = invenio_oauthclient.oauth.register_user(
            send_register_msg=True, **user_info
        )
        return user
