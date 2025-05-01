#!/bin/bash

rm -f /opt/invenio/var/instance/saml_cert.crt
rm -f /opt/invenio/var/instance/saml_private_key.key
echo "$SAML_CERT" > /opt/invenio/var/instance/saml_cert.crt
echo "$SAML_KEY" > /opt/invenio/var/instance/saml_private_key.key

exec uwsgi --ini /opt/invenio/var/instance/uwsgi_ui.ini
