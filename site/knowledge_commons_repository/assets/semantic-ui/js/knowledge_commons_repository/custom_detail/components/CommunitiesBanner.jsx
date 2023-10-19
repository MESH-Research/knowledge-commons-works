import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

const CommunitiesBanner = ({ community, isPreviewSubmissionRequest }) => {
  const isCommunityRestricted = community
    ? community.access.visibility == "restricted"
    : false;
  return (
    !isPreviewSubmissionRequest &&
    community && (
      <div
        id="communities"
        className="sidebar-container"
        aria-label={i18next.t("Record communities")}
      >
        <div className="ui container page-subheader bottom attached segment rdm-sidebar pr-0 pt-0">
          <div className="page-subheader-element ">
            <img
              className="ui tiny image community-header-logo has-placeholder"
              src={community.links.logo}
              alt=""
            />
          </div>
          <div className="page-subheader-element">
            <a href={community.links.logo.replace("/logo", community.slug)}>
              {" "}
              {community.metadata.title}
            </a>
            {isCommunityRestricted && (
              <span
                className="ui label horizontal small access-status restricted rel-ml-1"
                title={i18next.t("Community visibility")}
                data-tooltip={i18next.t(
                  "The community is restricted to users with access."
                )}
                data-inverted=""
              >
                <i className="icon ban" aria-hidden="true"></i>{" "}
                {i18next.t("Restricted")}
              </span>
            )}
          </div>
        </div>
      </div>
    )
  );
};

export { CommunitiesBanner };
