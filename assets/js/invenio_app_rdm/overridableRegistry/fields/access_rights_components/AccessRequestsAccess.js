// This file is part of Knowledge Commons Works
// Copyright (C) 2026 MESH Research
//
// Knowledge-Commons-Works is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import PropTypes from "prop-types";
import React, { useState } from "react";
import { useFormikContext, getIn } from "formik";
import { useSelector } from "react-redux";
import { Button, Checkbox, Form, Message } from "semantic-ui-react";
import { http, withCancel } from "react-invenio-forms";
import { i18next } from "@translations/i18next";
import { ShareModal } from "./ShareModal";

const SETTINGS_FIELD_PATH = "parent.access.settings";

/**
 * Deposit-sidebar control for access-request settings.
 *
 * Toggle persists immediately via ``PUT record.links.access`` (parent.access is
 * dump-only on draft save). Settings opens the share modal on the Settings tab.
 */
export const AccessRequestsAccess = ({ access, metadataOnly }) => {
  const { values, setFieldValue } = useFormikContext();
  const record = useSelector((state) => state.deposit.record) ?? {};
  const permissions = useSelector((state) => state.deposit.permissions) ?? {};
  const groupsEnabled =
    useSelector((state) => state.deposit.config?.groups_enabled) ?? false;

  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const recordPublic = access?.record === "public";
  const filesPublic = access?.files === "public";
  // Access requests only apply to public metadata + restricted files.
  const filesRestricted = !metadataOnly && recordPublic && !filesPublic;

  const settings = getIn(values, SETTINGS_FIELD_PATH) ?? {};
  const allowUserRequests = Boolean(settings.allow_user_requests);
  const allowGuestRequests = Boolean(settings.allow_guest_requests);
  const requestsEnabled = allowUserRequests || allowGuestRequests;

  const accessLink = values?.links?.access || record?.links?.access;
  const canManage = Boolean(permissions?.can_manage);
  const controlsDisabled = loading || !accessLink || !canManage;

  const recordForShare = {
    ...record,
    links: values.links || record.links,
    expanded: values.expanded ?? record.expanded,
    parent: {
      ...(record.parent || {}),
      access: {
        ...(record.parent?.access || {}),
        settings: {
          allow_user_requests: allowUserRequests,
          allow_guest_requests: allowGuestRequests,
          accept_conditions_text: settings.accept_conditions_text ?? null,
          secret_link_expiration: settings.secret_link_expiration ?? 0,
        },
      },
    },
  };

  const applySettings = (nextSettings) => {
    setFieldValue(SETTINGS_FIELD_PATH, {
      ...settings,
      ...nextSettings,
    });
  };

  const persistSettings = async (nextSettings) => {
    if (!accessLink) {
      setError(
        i18next.t(
          "Access request settings cannot be saved until the deposit has an access API link."
        )
      );
      return;
    }

    const previous = { ...settings };
    const payload = {
      allow_user_requests:
        nextSettings.allow_user_requests ?? allowUserRequests,
      allow_guest_requests:
        nextSettings.allow_guest_requests ?? allowGuestRequests,
      accept_conditions_text: settings.accept_conditions_text ?? null,
      secret_link_expiration: settings.secret_link_expiration ?? 0,
    };

    setLoading(true);
    setError(null);
    applySettings(payload);

    try {
      const cancellable = withCancel(http.put(accessLink, payload));
      const response = await cancellable.promise;
      const saved = response?.data?.parent?.access?.settings ?? payload;
      applySettings(saved);
    } catch (err) {
      applySettings(previous);
      setError(
        err?.response?.data?.message ||
          err?.message ||
          i18next.t("Unable to update access request settings.")
      );
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (_e, { checked }) => {
    if (checked) {
      persistSettings({
        allow_user_requests: true,
        allow_guest_requests: allowGuestRequests,
      });
    } else {
      persistSettings({
        allow_user_requests: false,
        allow_guest_requests: false,
      });
    }
  };

  const handleRecordUpdate = (updatedRecord) => {
    const updatedSettings = updatedRecord?.parent?.access?.settings;
    if (updatedSettings) {
      applySettings(updatedSettings);
    }
  };

  if (!filesRestricted) {
    return null;
  }

  return (
    <>
      <Form.Field className="mb-0 rel-mt-1">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "0.5rem",
          }}
        >
          <Checkbox
            id="access-requests-enabled"
            data-testid="access-requests-toggle"
            label={i18next.t("Allow access requests")}
            checked={requestsEnabled}
            disabled={controlsDisabled}
            onChange={handleToggle}
          />
          <Button
            type="button"
            size="mini"
            basic
            icon="cog"
            content={i18next.t("Settings")}
            disabled={controlsDisabled}
            onClick={() => setModalOpen(true)}
            aria-haspopup="dialog"
            className="ml-5"
          />
        </div>
        {error && (
          <Message negative size="tiny" content={error} className="mt-5" />
        )}
      </Form.Field>

      {modalOpen && (
        <ShareModal
          open={modalOpen}
          handleClose={() => setModalOpen(false)}
          record={recordForShare}
          permissions={permissions}
          groupsEnabled={groupsEnabled}
          defaultTabKey="accessRequests"
          onRecordUpdate={handleRecordUpdate}
        />
      )}
    </>
  );
};

AccessRequestsAccess.propTypes = {
  access: PropTypes.object.isRequired,
  metadataOnly: PropTypes.bool,
};

AccessRequestsAccess.defaultProps = {
  metadataOnly: false,
};
