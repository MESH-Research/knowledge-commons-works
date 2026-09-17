// This file is part of Knowledge Commons Works
//
// Based on a file in Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2026 MESH Research
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _isEmpty from "lodash/isEmpty";
import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import { TextAreaField } from "react-invenio-forms";
import { Card, Form, List } from "semantic-ui-react";
import { EmbargoCheckboxField } from "./EmbargoCheckboxField.js";
import { EmbargoDateField } from "./EmbargoDateField";
import { i18next } from "@translations/i18next";

export const EmbargoAccess = ({ access, accessCommunity, metadataOnly }) => {
  const recordPublic = access.record === "public";
  const communityPublic = accessCommunity === "public";

  const embargoActive = access.embargo?.active || false;
  const embargoUntil = access.embargo?.until;
  const embargoReason = access.embargo?.reason;
  const embargoWasLifted = !embargoActive && !_isEmpty(embargoUntil);
  // Community must be public. With files, enabling embargo auto-restricts files.
  // Metadata-only deposits still need the record itself restricted.
  const embargoEnabled = communityPublic && (!metadataOnly || !recordPublic);

  const fmtDate = embargoUntil
    ? DateTime.fromISO(embargoUntil).toLocaleString(DateTime.DATE_FULL)
    : "???";

  return (
    <>
      <Form.Field className="mb-0 rel-mt-1">
        <EmbargoCheckboxField
          fieldPath="access.embargo.active"
          disabled={!embargoEnabled}
          label={i18next.t("Apply an embargo")}
          checked={!!embargoActive}
        />
      </Form.Field>

      {embargoActive && (
        <Card className="transparent rel-pt-1 p-15">
          <List divided relaxed>
            <List.Content>
              <List.Header as="label" htmlFor="access.embargo.active"></List.Header>

              <EmbargoDateField fieldPath="access.embargo.until" required classnames="rel-mt-1" />
              <TextAreaField
                label={i18next.t("Embargo reason")}
                fieldPath="access.embargo.reason"
                placeholder={i18next.t("Optionally, describe the reason for the embargo.")}
                optimized="true"
                className="rel-mt-1"
              />
              {embargoWasLifted && (
                <>
                  <p>
                    {i18next.t(`Embargo was lifted on {{fmtDate}}.`, {
                      fmtDate: fmtDate,
                    })}
                  </p>
                  {embargoReason && (
                    <p>
                      <b>{i18next.t("Reason")}</b>: {embargoReason}.
                    </p>
                  )}
                </>
              )}
            </List.Content>
          </List>
        </Card>
      )}
    </>
  );
};

EmbargoAccess.propTypes = {
  access: PropTypes.object.isRequired,
  metadataOnly: PropTypes.bool,
  accessCommunity: PropTypes.string.isRequired,
};

EmbargoAccess.defaultProps = {
  metadataOnly: false,
};
