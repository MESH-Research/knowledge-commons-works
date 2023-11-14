import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

const DraftBackButton = ({
  backPage,
  isPreview,
  isDraft,
  canManage,
  isPreviewSubmissionRequest,
  show,
}) => {
  return isPreview && !isPreviewSubmissionRequest && canManage && isDraft ? (
    <nav
      className={`back-navigation rel-pb-2 pl-0 ${show}`}
      aria-label={i18next.t("Back-navigation")}
    >
      <a className="ui button labeled icon basic orange" href={backPage}>
        <i className="ui icon angle left"></i> {i18next.t("Back to edit")}
      </a>
    </nav>
  ) : (
    ""
  );
};

export { DraftBackButton };
