// This file is part of Knowledge Commons Works
// Adapted from the component in Invenio-RDM-Records
// Copyright (C) 2026 MESH Research
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2021 Graz University of Technology.
//
// Knowledge-Commons-Works and Invenio-RDM-Records are free software; you can
// redistribute it and/or modify it under the terms of the MIT License; see
// LICENSE file for more details.

import React from "react";
import { useSelector } from "react-redux";
import PropTypes from "prop-types";
import { useFormikContext, getIn } from "formik";
import { Card, Divider, Form } from "semantic-ui-react";
import { i18next } from "@translations/i18next";
import {
  MetadataAccess,
  FilesAccess,
  EmbargoAccess,
  AccessMessage,
} from "./access_rights_components";

const AccessRightField = ({
  fieldPath,
  allowRecordRestriction = true,
  icon = undefined,
  label = i18next.t("Access Permissions"),
  record = {},
  recordRestrictionGracePeriod = undefined,
  showMetadataAccess = undefined,
}) => {
  /** Top-level Access Right Component */
  const community = useSelector((s) => s.deposit.editorState.selectedCommunity);
  const files = useSelector((s) => s.files);

  const isGhostCommunity = community?.is_ghost === true;
  const communityAccess =
    (community && !isGhostCommunity && community.access.visibility) || "public";
  const { values } = useFormikContext();
  const isMetadataOnly = !record.files.enabled || Object.entries(files.entries).length < 1;

  return (
    <>
      <AccessMessage
        access={getIn(values, fieldPath)}
        accessCommunity={communityAccess}
        metadataOnly={isMetadataOnly}
      />
      <Card label={label} id="visibility-section" className="access-right pr-5 pl-5">
        <Form.Field required>
          {label ? (
            <Card.Content className="p-0">
              <Card.Header>
                <label htmlFor={fieldPath} className="field-label-class invenio-field-label">
                  {label}
                  {icon && <i className={`${icon} icon`} />}
                </label>
              </Card.Header>
            </Card.Content>
          ) : null}
          <Card.Content className="p-0">
            {showMetadataAccess && (
              <>
                <MetadataAccess
                  recordAccess={getIn(values, `${fieldPath}.record`)}
                  communityAccess={communityAccess}
                  record={record}
                  recordRestrictionGracePeriod={recordRestrictionGracePeriod}
                  allowRecordRestriction={allowRecordRestriction}
                />
              </>
            )}

            <FilesAccess
              access={getIn(values, fieldPath)}
              accessCommunity={communityAccess}
              metadataOnly={isMetadataOnly}
            />
            <EmbargoAccess
              access={getIn(values, fieldPath)}
              accessCommunity={communityAccess}
              metadataOnly={isMetadataOnly}
            />
          </Card.Content>
        </Form.Field>
      </Card>
    </>
  );
};

AccessRightField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  icon: PropTypes.string,
  allowRecordRestriction: PropTypes.bool,
  record: PropTypes.object,
  recordRestrictionGracePeriod: PropTypes.number,
  showMetadataAccess: PropTypes.bool,
};

export { AccessRightField };
