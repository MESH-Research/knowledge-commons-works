# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

from marshmallow import Schema, fields

"""Configuration variables related to users and accounts."""

# isort: split

# DEPRECATED
# These sub-schemas are deprecated for now because the profile
# search mapping only allows for keyword fields.
# class CustomAffiliationSchema(Schema):
#     """The default affiliations schema."""

#     name = fields.String()
#     id = fields.String()


# class CustomNamePartsSchema(Schema):
#     """The default name parts schema."""

#     first = fields.String()
#     middle = fields.String()
#     last = fields.String()
#     last_prefix_for_alphabetizing = fields.String()
#     last_prefix = fields.String()
#     patronymic = fields.String()
#     suffix = fields.String()


# class CustomUserIdentifierSchema(Schema):
#     """The default user identifier schema."""

#     identifier = fields.String()
#     scheme = fields.String()


class CustomUserProfileSchema(Schema):
    """The default user profile schema."""

    full_name = fields.String()
    affiliations = fields.String()
    name_parts = fields.String()
    name_parts_local = fields.String()
    identifier_email = fields.String()
    identifier_orcid = fields.String()
    identifier_kc_username = fields.String()
    identifier_other = fields.String()
    unread_notifications = fields.String()


ACCOUNTS_USER_PROFILE_SCHEMA = CustomUserProfileSchema()
