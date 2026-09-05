// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Modified for Knowledge Commons Works
// Copyright (C) 2024-2025 Mesh Research
//
// Invenio-RDM-Records and Knowledge-Commons-Works are free software;
// you can redistribute and/or modify them under the terms of the MIT
// License; see LICENSE file for more details.

import { DateTime } from "luxon";
import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/i18next";
import { Trans } from "react-i18next";
import { Icon, Message } from "semantic-ui-react";

export const AccessMessage = ({ access, metadataOnly, accessCommunity }) => {
  const recordPublic = access.record === "public";
  const filesPublic = access.files === "public";
  const communityPublic = accessCommunity === "public";
  const embargoActive = access.embargo?.active || false;

  // restriction logic
  const fullyRestricted = !communityPublic || (!recordPublic && !embargoActive);
  const fullyPublic = communityPublic && recordPublic && (metadataOnly || filesPublic);

  const embargoedFiles = embargoActive && !filesPublic && recordPublic;
  const restrictedFiles = !embargoActive && !filesPublic && recordPublic;
  const fullEmbargo = !recordPublic && embargoActive;

  const fmtDate = access.embargo?.until
    ? DateTime.fromISO(access.embargo.until).toLocaleString(DateTime.DATE_FULL)
    : "[date not yet set]";

  if (fullyPublic) {
    return (
      <Message positive visible data-testid="access-message" attached="top">
        <Message.Content>
          <Message.Header className="mb-5">
            {i18next.t("Public")}
            <Icon name="lock open mr-5" />
          </Message.Header>

          {metadataOnly
            ? i18next.t("The record is publicly accessible.")
            : i18next.t("The record and files are publicly accessible.")}
        </Message.Content>
      </Message>
    );
  }

  if (fullEmbargo) {
    return (
      <Message warning visible data-testid="access-message">
        <Message.Content>
          <Message.Header className="mb-5">
            {i18next.t("Embargoed access")}
            <Icon name="lock mb-5" />
          </Message.Header>
          <Trans
            defaults="On <bold>{{fmtDate}}</bold> the record will automatically be made publicly accessible. Until then, the record can <bold>only</bold> be accessed by <bold>users specified</bold> in the permissions."
            values={{ fmtDate }}
            components={{ bold: <b /> }}
          />
        </Message.Content>
      </Message>
    );
  }

  if (fullyRestricted) {
    return (
      <Message negative visible data-testid="access-message">
        <Message.Content>
          <Message.Header className="mb-5">
            {i18next.t("Access Restricted")}
            <Icon name="lock mb-5" />
          </Message.Header>
          <Trans>
            The record can <b>only</b> be accessed by <b>users specified</b> in the permissions.
          </Trans>
        </Message.Content>
      </Message>
    );
  }

  if (restrictedFiles) {
    return (
      <Message warning visible data-testid="access-message">
        <Message.Content>
          <Message.Header className="mb-5">
            {i18next.t("Files restricted")}
            <Icon name="lock mb-5" />
          </Message.Header>
          <Trans>
            The record is publicly accessible. The files can <b>only</b> be accessed by{" "}
            <b>users specified</b> in the permissions.
          </Trans>
        </Message.Content>
      </Message>
    );
  }

  if (embargoedFiles) {
    return (
      <Message warning visible data-testid="access-message">
        <Message.Content>
          <Message.Header className="mb-5">
            {i18next.t("Files embargoed")}
            <Icon name="lock mb-5" />
          </Message.Header>
          <Trans
            defaults="The record is publicly accessible. On <bold>{{ date }}</bold> the files will automatically be made publicly accessible. Until then, the files can <bold>only</bold> be accessed by <bold>users specified</bold> in the permissions."
            values={{ date: fmtDate }}
            components={{ bold: <b /> }}
          />
        </Message.Content>
      </Message>
    );
  }
};

AccessMessage.propTypes = {
  access: PropTypes.object.isRequired,
  metadataOnly: PropTypes.bool,
  accessCommunity: PropTypes.string.isRequired,
};

AccessMessage.defaultProps = {
  metadataOnly: false,
};
