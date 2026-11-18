// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Modified for Knowledge Commons Works
// Copyright (C) 2024-2026 Mesh Research
//
// Invenio-RDM-Records and Knowledge-Commons-Works are free software;
// you can redistribute and/or modify them under the terms of the MIT
// License; see LICENSE file for more details.

import { DateTime } from "luxon";
import React, { useCallback, useState } from "react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import { useSelector } from "react-redux";
import { i18next } from "@translations/i18next";
import { Trans } from "react-i18next";
import { Icon, Message } from "semantic-ui-react";
import { DepositShareModal } from "@js/invenio_modular_deposit_form/field_components/patched/rdm_fields/share_components/DepositShareModal";
import {
  buildRecordForModal,
  fillMissingFromRedux,
  mergeShareRecordIntoFormik,
} from "@js/invenio_modular_deposit_form/field_components/patched/rdm_fields/share_components/depositShareRecord";

const USERS_SPECIFIED_LINK_STYLE = {
  fontWeight: "bold",
  textDecoration: "underline dotted",
  textUnderlineOffset: "0.15em",
  background: "none",
  border: "none",
  padding: 0,
  margin: 0,
  color: "inherit",
  cursor: "pointer",
  font: "inherit",
};

/**
 * Same visibility gate as the deposit-form Share button
 * (`record.parent && (is_draft === null || can_manage)`).
 *
 * @param {object} record
 * @param {object} permissions
 * @returns {boolean}
 */
export const canShowShareAccessLink = (record, permissions) =>
  Boolean(record?.parent) &&
  (record?.is_draft === null || Boolean(permissions?.can_manage));

/**
 * Bold dotted-underline control that opens the deposit share modal.
 *
 * @param {object} props
 * @param {React.ReactNode} props.children
 */
const UsersSpecifiedShareLink = ({ children }) => {
  const { values, setValues } = useFormikContext();
  const record = useSelector((state) => state.deposit.record) ?? {};
  const permissions = useSelector((state) => state.deposit.permissions) ?? {};
  const groupsEnabled =
    useSelector((state) => state.deposit.config?.groups_enabled) ?? false;
  const [modalOpen, setModalOpen] = useState(false);

  const handleRecordChangeFromModal = useCallback(
    (modalRecord) => {
      setValues(mergeShareRecordIntoFormik(values, modalRecord));
    },
    [setValues, values]
  );

  const handleOpen = (event) => {
    event.preventDefault();
    const filled = fillMissingFromRedux(values, record);
    if (filled !== values) {
      setValues(filled);
    }
    setModalOpen(true);
  };

  const recordForModal = buildRecordForModal(
    fillMissingFromRedux(values, record)
  );

  return (
    <>
      <button
        type="button"
        onClick={handleOpen}
        style={USERS_SPECIFIED_LINK_STYLE}
        aria-haspopup="dialog"
        data-testid="users-specified-share-link"
      >
        {children}
      </button>
      {modalOpen && (
        <DepositShareModal
          open
          handleClose={() => setModalOpen(false)}
          record={recordForModal}
          permissions={permissions}
          groupsEnabled={groupsEnabled}
          onRecordChange={handleRecordChangeFromModal}
        />
      )}
    </>
  );
};

UsersSpecifiedShareLink.propTypes = {
  children: PropTypes.node,
};

const restrictedMessageComponents = {
  bold: <b />,
  usersLink: <UsersSpecifiedShareLink />,
};

/**
 * Restricted-access body copy. After Share is available, "users specified"
 * opens the share modal; before draft save, explain that sharing comes later.
 *
 * @param {object} props
 * @param {string} props.withShareDefaults - Trans defaults when Share is shown
 * @param {string} props.beforeSaveDefaults - Trans defaults before Share is shown
 * @param {object} [props.values] - Trans interpolation values
 */
const RestrictedAccessBody = ({ withShareDefaults, beforeSaveDefaults, values }) => {
  const record = useSelector((state) => state.deposit.record) ?? {};
  const permissions = useSelector((state) => state.deposit.permissions) ?? {};
  const shareAvailable = canShowShareAccessLink(record, permissions);

  return (
    <Trans
      defaults={shareAvailable ? withShareDefaults : beforeSaveDefaults}
      values={values}
      components={restrictedMessageComponents}
    />
  );
};

RestrictedAccessBody.propTypes = {
  withShareDefaults: PropTypes.string.isRequired,
  beforeSaveDefaults: PropTypes.string.isRequired,
  values: PropTypes.object,
};

export const AccessMessage = ({
  access,
  metadataOnly,
  accessCommunity,
  attached,
}) => {
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
      <Message positive visible attached={attached} data-testid="access-message">
        <Message.Content>
          <Message.Header className="mb-5">
            {i18next.t("Public")}
            <Icon name="lock open" className="ml-10" />
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
      <Message warning visible attached={attached} data-testid="access-message">
        <Message.Content>
          <Message.Header className="mb-5">
            {i18next.t("Embargoed access")}
            <Icon name="lock" className="ml-10" />
          </Message.Header>
          <RestrictedAccessBody
            values={{ fmtDate }}
            withShareDefaults="On <bold>{{fmtDate}}</bold> the record will automatically be made publicly accessible. Until then, the record can <bold>only</bold> be accessed by <usersLink>users specified</usersLink> in the permissions."
            beforeSaveDefaults="On <bold>{{fmtDate}}</bold> the record will automatically be made publicly accessible. Until then, the record can <bold>only</bold> be accessed by specified users once a draft has been saved."
          />
        </Message.Content>
      </Message>
    );
  }

  if (fullyRestricted) {
    return (
      <Message negative visible attached={attached} data-testid="access-message">
        <Message.Content>
          <Message.Header className="mb-5">
            {i18next.t("Access Restricted")}
            <Icon name="lock" className="ml-10" />
          </Message.Header>
          <RestrictedAccessBody
            withShareDefaults="The record can <bold>only</bold> be accessed by <usersLink>users specified</usersLink> in the permissions."
            beforeSaveDefaults="The record can <bold>only</bold> be accessed by specified users once a draft has been saved."
          />
        </Message.Content>
      </Message>
    );
  }

  if (restrictedFiles) {
    return (
      <Message warning visible attached={attached} data-testid="access-message">
        <Message.Content>
          <Message.Header className="mb-5">
            {i18next.t("Files restricted")}
            <Icon name="lock" className="ml-10" />
          </Message.Header>
          <RestrictedAccessBody
            withShareDefaults="The record is publicly accessible. The files can <bold>only</bold> be accessed by <usersLink>users specified</usersLink> in the permissions."
            beforeSaveDefaults="The record is publicly accessible. The files can <bold>only</bold> be accessed by specified users once a draft has been saved."
          />
        </Message.Content>
      </Message>
    );
  }

  if (embargoedFiles) {
    return (
      <Message warning visible attached={attached} data-testid="access-message">
        <Message.Content>
          <Message.Header className="mb-5">
            {i18next.t("Files embargoed")}
            <Icon name="lock" className="ml-10" />
          </Message.Header>
          <RestrictedAccessBody
            values={{ date: fmtDate }}
            withShareDefaults="The record is publicly accessible. On <bold>{{ date }}</bold> the files will automatically be made publicly accessible. Until then, the files can <bold>only</bold> be accessed by <usersLink>users specified</usersLink> in the permissions."
            beforeSaveDefaults="The record is publicly accessible. On <bold>{{ date }}</bold> the files will automatically be made publicly accessible. Until then, the files can <bold>only</bold> be accessed by specified users once a draft has been saved."
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
  attached: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
};

AccessMessage.defaultProps = {
  metadataOnly: false,
  attached: undefined,
};
