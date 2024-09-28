from invenio_saml.handlers import acs_handler_factory

test_config_saml = {
    "SSO_SAML_IDPS": {
        # name your authentication provider
        "knowledgeCommons": {
            # Basic info
            "title": "Knowledge Commons",
            "description": "Knowledge Commons Authentication Service",
            # "icon": "",
            # path to the file i.e. "./saml/sp.crt"
            "sp_cert_file": "./docker/nginx/samlCertificate.crt",
            # path to the file i.e. "./saml/sp.key"
            "sp_key_file": "./docker/nginx/samlPrivateKey.key",
            "settings": {
                # If strict is True, then the Python Toolkit will
                # reject unsigned
                # or unencrypted messages if it expects them to be signed
                # or encrypted.
                # Also it will reject the messages if the SAML standard is
                # not strictly
                # followed. Destination, NameId, Conditions ... are
                # validated too.
                "strict": False,
                # Enable debug mode (outputs errors).
                # TODO: change before production
                "debug": True,
                # Service Provider Data that we are deploying.
                "sp": {
                    # NOTE: Assertion consumer service is
                    # https://localhost/saml/
                    # authorized/knowledgeCommons
                    # NOTE: entityId for the dev SP is
                    # https://localhost/saml/metadata/knowledgeCommons
                    # NOTE: entityId for the staging SP is
                    # https://invenio-dev.hcommons-staging.org/saml/idp
                    # Specifies the constraints on the name identifier to
                    # be used
                    # to represent the requested subject.
                    # Take a look on https://github.com/onelogin/python-saml/
                    # blob/master/src/onelogin/saml2/constants.py
                    # to see the NameIdFormat that are supported.
                    "NameIDFormat": (
                        "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
                    ),
                },
                # Identity Provider Data that we want connected with our SP.
                "idp": {
                    # Identifier of the IdP entity  (must be a URI)
                    "entityId": "https://proxy.hcommons-dev.org/idp",
                    # SSO endpoint info of the IdP. (Authentication
                    # Request protocol)
                    "singleSignOnService": {
                        # URL Target of the IdP where the Authentication
                        # Request Message will be sent.
                        "url": (
                            "https://proxy.hcommons-dev.org/Saml2/sso/redirect"
                        ),
                        # SAML protocol binding to be used when returning the
                        # <Response> message. OneLogin Toolkit supports
                        # the HTTP-Redirect binding
                        # only for this endpoint.
                        "binding": (
                            "urn:oasis:names:tc:SAML:2.0:bindings:"
                            "HTTP-Redirect"
                        ),
                    },
                    # SLO endpoint info of the IdP.
                    "singleLogoutService": {
                        # URL Location where the <LogoutRequest> from the IdP
                        # will be sent (IdP-initiated logout)
                        "url": "https://localhost/saml/slo/knowledgeCommons",
                        # SAML protocol binding to be used when returning
                        # the <Response> message. OneLogin Toolkit supports
                        # the HTTP-Redirect binding
                        # only for this endpoint.
                        "binding": (
                            "urn:oasis:names:tc:SAML:2.0:bindings:"
                            "HTTP-Redirect"
                        ),
                    },
                    # Public X.509 certificate of the IdP
                    "x509cert": (
                        "MIIELTCCApWgAwIBAgIJAPeDxhrttBXNMA0GCSqGSIb3DQEBCwUAMCExHzAdBgNVBAMTFnByb3h5Lmhjb21tb25zLWRldi5vcmcwHhcNMTcxMTAxMTc0NTE3WhcNMjcxMDMwMTc0NTE3WjAhMR8wHQYDVQQDExZwcm94eS5oY29tbW9ucy1kZXYub3JnMIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEA0d6ycqcxviv946IzS7ZobCK0XAsrwHvcKo65hWkOZsxYBTRvjKITSpKv4TGyVG4leI0Ifthz7o3QAA4IKkkgY15kYO5AhJc9pVa+11vG0DM58qO6yraQRM4U/71AgDEmEZXsUblf3TCkN5w351G26jNwgax+aWNuwzX5EDS5farOhruGG2FwVYEOEHOtWSOKBR8duq1O/yY9OKMhIc2kmh9R"  # noqa: E501
                        " m1594qTzZbxNXjyCY+LU/GZbYQP+WlbjM/dHflK5Y2WexyT942xHYnesvPnzGvEMB4g685Yyjl+9xz+AE41sifKYy03m7GgkimXNxQ2SnGZ4Rtj+3DlDC9S/dB2CRJd2uaTwgxEEK/zJJ1K2TFRfDH/wxCW5DwI3n8BMglc8TPZ33FDqNgZPwPDl92/shwNIU3sFM/lmDtLm/4XeKZjOZYa+WCVC71tnFYDltK1//oAqFSVRF0WT6+dcnjXxJSdRrQo+C1gWI+aXJzmDmhp8WBN2q7nUGapJYSu0a5yXAgMBAAGjaDBmMEUGA1UdEQQ+MDyCFnByb3h5Lmhjb21tb25zLWRldi5vcmeGImh0dHBzOi8vcHJveHkuaGNvbW1vbnMtZGV2Lm9yZy9pZHAwHQYDVR0OBBYEFDLkys52MyePCpr5IN2ybhgIosmlMA0GCSqGSIb3DQEBCwUAA4IBgQDOuUnSwfru5uNorAISo5QEVUi3UrholF0RPFFvM6P63MOpWZwdFQYKjY1eaaE+X++AZ1FkHQv/esy7F0FRWiyU3LHUX3Yzuttb7vj7mw5D6IYuSIG1/0Edj/eSpnOs+6MQUUpfaFi+A0C9Smng6L1kj3SOlePprJdwfIdGG/6oiDaF1bhoWs/eidouzMLMKiGY6KzmaT8fInST1BGMdm4+zqNvwd1FuifDOvVQqqtl"  # noqa: E501
                        " q2og0arTXG01YyCvU+NJT/6KjLDZf1bSmDWAPQ51Fc4fpkeOj+aG0DfwdutO2SNkdDDdD/m7pnepxv2u8jqSKyYKdrzLd0lJPrqH8YV4AYmyJ1UortJXFoTsGSbPv0fw"  # noqa: E501
                        " qM1b1JAKsPMP22xmp2i4BcYOT1jZ+R+RXmMNK+fUSXAmSkhk/8h6CMgmU4ldBj5jtyn/M4GrGesMU1sIgidoCj/5F3jQlswz0eoaX3LyWQkDZbUbIm6Vz4h3GFwwlky8c5RbLEmwlolP+zSzoq4T/tw="  # noqa: E501
                    ),
                },
                # Security settings
                # more on https://github.com/onelogin/python-saml
                "security": {
                    "authnRequestsSigned": False,
                    "failOnAuthnContextMismatch": False,
                    "logoutRequestSigned": False,
                    "logoutResponseSigned": False,
                    "metadataCacheDuration": None,
                    "metadataValidUntil": None,
                    "nameIdEncrypted": False,
                    "requestedAuthnContext": False,
                    "requestedAuthnContextComparison": "exact",
                    "signMetadata": False,
                    "signatureAlgorithm": (
                        "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
                    ),
                    "wantAssertionsEncrypted": False,
                    "wantAssertionsSigned": False,
                    "wantAttributeStatement": False,
                    "wantMessagesSigned": False,
                    "wantNameId": True,
                    "wantNameIdEncrypted": False,
                    "digestAlgorithm": (
                        "http://www.w3.org/2001/04/xmlenc#sha256"
                    ),
                },
            },
            # Account Mapping
            "mappings": {
                "email": "urn:oid:0.9.2342.19200300.100.1.3",  # "mail"
                # "name": "urn:oid:2.5.4.3",  # "cn"
                "name": "urn:oid:2.5.4.42",  # "givenName"
                "surname": "urn:oid:2.5.4.4",  # "sn"
                "external_id": (
                    "urn:oid:2.16.840.1.113730.3.1.3"
                ),  # "employeeNumber"
            },  # FIXME: new entity id url, assertion consumer service url,
            # certificate
            # "title", 'urn:oid:2.5.4.12': ['Hc Developer'],
            # 'urn:oid:2.16.840.1.113730.3.1.3': ['iscott'],
            # 'urn:oid:0.9.2342.19200300.100.1.1':
            #   ['100103028069838784737+google.com@commons.mla.org'],
            # "isMemberOf", 'urn:oid:1.3.6.1.4.1.5923.1.5.1.1':
            #   ['CO:COU:HC:members:active'],
            # 'urn:oid:1.3.6.1.4.1.49574.110.13':
            #   ['https://google-gateway.hcommons-dev.org/idp/shibboleth'],
            # 'urn:oid:1.3.6.1.4.1.49574.110.10': ['Google login'],
            # 'urn:oid:1.3.6.1.4.1.49574.110.11': ['Humanities Commons'],
            # 'urn:oid:1.3.6.1.4.1.49574.110.12': ['Humanities Commons']}
            # Inject your remote_app to handler
            # Note: keep in mind the string should match
            # given name for authentication provider
            "acs_handler": acs_handler_factory("knowledgeCommons"),
            # Automatically set `confirmed_at` for users upon
            # registration, when using the default `acs_handler`
            "auto_confirm": True,
        }
    }
}
