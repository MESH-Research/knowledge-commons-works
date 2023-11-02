import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { BadgesFormatsList } from "../components/BadgesFormatsList";

const Doi = ({ idDoi, doiBadgeUrl, doiLink }) => {
  return (
    <>
      <span
        className="get-badge"
        data-toggle="tooltip"
        data-placement="bottom"
        style={{ cursor: "pointer" }}
        title={i18next.t("Get the DOI badge!")}
      >
        <img
          id="record-doi-badge"
          data-target={`[data-modal='${idDoi}']`}
          src={doiBadgeUrl}
          alt={idDoi}
        />
      </span>

      <div
        id="doi-modal"
        className="ui modal fade badge-modal"
        data-modal={idDoi}
      >
        <div className="header">{i18next.t("DOI Badge")}</div>
        <div className="content">
          <h4>
            <small>{i18next.t("DOI")}</small>
          </h4>
          <h4>
            <pre>{idDoi}</pre>
          </h4>
          <BadgesFormatsList imageFilename={doiBadgeUrl} target={doiLink} />
        </div>
      </div>
    </>
  );
};

export { Doi };
