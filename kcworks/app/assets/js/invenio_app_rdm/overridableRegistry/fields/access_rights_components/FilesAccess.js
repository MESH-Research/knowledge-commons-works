// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React from "react";
import { ProtectionButtons } from "./ProtectionButtons";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Card, Form, Icon } from "semantic-ui-react";

export const FilesAccess = ({ access, accessCommunity, metadataOnly }) => {
  const publicFiles = access.files === "public";
  const publicMetadata = access.record === "public";
  const publicCommunity = accessCommunity === "public";

  const fullRecordRestricted = !publicCommunity || !publicMetadata;
  const filesRestricted = publicCommunity && !publicFiles && publicMetadata;

  const filesButtonsDisplayed = !metadataOnly && publicCommunity && publicMetadata;

  if (metadataOnly) {
    return (null
      // <Card.Meta data-testid="access-files">
      // <em>{i18next.t("The record has no files.")}</em>
      // </Card.Meta>
    );
  }

  return (
    <>
      {filesButtonsDisplayed && (
        <Form.Field>
          <label htmlFor="access.files" className="invenio-field-label">
            <Icon name="lock" />
            {i18next.t("Files access")}
          </label>
          <ProtectionButtons
            active={publicFiles}
            disable={!publicCommunity}
            fieldPath="access.files"
          />
        </Form.Field>
      )}
      {/* {fullRecordRestricted && (
        <Card.Description>
          <em>{i18next.t("The deposit record is restricted.")}</em>
        </Card.Description>
      )}
      {filesRestricted && (
        <Card.Description>
          <em>{i18next.t("The files of this record are restricted.")}</em>
        </Card.Description>
      )} */}
    </>
  );
};

FilesAccess.propTypes = {
  access: PropTypes.object.isRequired,
  metadataOnly: PropTypes.bool,
  accessCommunity: PropTypes.string.isRequired,
};

FilesAccess.defaultProps = {
  metadataOnly: false,
};
