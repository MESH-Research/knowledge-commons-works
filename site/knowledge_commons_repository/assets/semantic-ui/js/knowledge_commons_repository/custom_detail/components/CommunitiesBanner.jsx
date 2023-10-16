import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

const CommunitiesBanner = ({ community, isPreviewSubmissionRequest }) => {
  const isCommunityRestricted = community
    ? community.access.visibility == "restricted"
    : false;
  return (
    !isPreviewSubmissionRequest &&
    community && (
      <div className="ui fluid container page-subheader-outer with-submenu compact ml-0-mobile mr-0-mobile">
        <div className="ui container page-subheader">
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
