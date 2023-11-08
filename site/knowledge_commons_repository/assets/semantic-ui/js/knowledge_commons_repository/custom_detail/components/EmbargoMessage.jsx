import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

const EmbargoMessage = ({ record }) => {
  return (
    <div
      className={`ui ${record.ui.access_status.message_class} message file-box-message`}
    >
      <i className={`ui ${record.ui.access_status.icon} icon`}></i>
      <b>{record.ui.access_status.title_l10n}</b>
      <p>{record.ui.access_status.description_l10n}</p>
      {!!record.access.embargo.reason ? (
        <p>
          {i18next.t("Why this restriction")}? {record.access.embargo.reason}
        </p>
      ) : (
        ""
      )}
    </div>
  );
};

export { EmbargoMessage };
