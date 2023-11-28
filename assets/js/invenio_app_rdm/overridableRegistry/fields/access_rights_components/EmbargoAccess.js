// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _isEmpty from "lodash/isEmpty";
import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import { TextAreaField } from "react-invenio-forms";
import { Button, Divider, Form, Icon, List } from "semantic-ui-react";
import { EmbargoDateField } from "./EmbargoDateField";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Trans } from "react-i18next";
import { useFormikContext } from "formik";

export const EmbargoAccess = ({ access, accessCommunity, metadataOnly }) => {
  const { setFieldValue } = useFormikContext();
  console.log("EmbargoAccess.js: access", access);
  const recordPublic = access.record === "public";
  const filesPublic = access.files === "public";
  const communityPublic = accessCommunity === "public";

  const filesRestricted = !metadataOnly && !filesPublic;

  const embargoActive = access.embargo?.active || false;
  const embargoUntil = access.embargo?.until;
  const embargoReason = access.embargo?.reason;
  const embargoWasLifted = !embargoActive && !_isEmpty(embargoUntil);
  const embargoEnabled = communityPublic && (!recordPublic || filesRestricted);

  const fmtDate = embargoUntil
    ? DateTime.fromISO(embargoUntil).toLocaleString(DateTime.DATE_FULL)
    : "???";

  const publicColor = !embargoActive ? "positive" : "";
  const restrictedColor = embargoActive ? "negative" : "";

  const handlePublicButtonClick = () => {
    setFieldValue('access.files', "public");
    setFieldValue("access.embargo", {
      active: false,
    });
  }

  const handleRestrictedButtonClick = () => {
    setFieldValue('access.files', "restricted");
    setFieldValue("access.embargo", {
      active: true,
    });
  }

  return (
    <>
    <Form.Field>
      <label htmlFor="access.embargo.active" className="invenio-field-label">
        <Icon name="clock outline" />
        {i18next.t("Apply an embargo")}
      </label>
      <Button.Group widths="2">
        <Button
          className={`${publicColor} {!embargoEnabled ? "disabled" : ""}`}
          disabled={!embargoEnabled}
          onClick={handlePublicButtonClick}
          active={!embargoActive}
        >
          {filesPublic ? i18next.t("Unrestricted") : i18next.t("Not time limited")}
        </Button>
        <Button
          active={embargoActive}
          onClick={handleRestrictedButtonClick}
          disabled={!embargoEnabled}
          className={`${restrictedColor} {!embargoEnabled ? "disabled" : ""}`}
        >
          {i18next.t("Embargoed")}
        </Button>
      </Button.Group>
          </Form.Field>

    <List divided relaxed>
        <List.Content>
          <List.Header as="label" htmlFor="access.embargo.active" >
          </List.Header>

          {!metadataOnly && filesPublic && !embargoActive && (
          <List.Description>
            <Trans>
              Record or files access must be <b>restricted</b> to apply an embargo.
            </Trans>
          </List.Description>
          )}

          {embargoActive && (
            <>
              <Divider hidden className="rel-mb-1" />
              <EmbargoDateField fieldPath="access.embargo.until" required />
              <TextAreaField
                label={i18next.t("Embargo reason")}
                fieldPath="access.embargo.reason"
                placeholder={i18next.t(
                  "Optionally, describe the reason for the embargo."
                )}
                optimized="true"
              />
            </>
          )}
          {embargoWasLifted && (
            <>
              <Divider hidden />
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
