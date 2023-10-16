import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

const CommunitiesBanner = ({ community, isPreviewSubmissionRequest }) => {
  const isCommunityRestricted = community.access.visibility == "restricted";
  return (
    !isPreviewSubmissionRequest &&
    community && (
      <div class="ui fluid container page-subheader-outer with-submenu compact ml-0-mobile mr-0-mobile">
        <div class="ui container page-subheader">
          <div class="page-subheader-element ">
            <img
              class="ui tiny image community-header-logo has-placeholder"
              src={community.links.logo}
              alt=""
            />
          </div>
          <div class="page-subheader-element">
            <a href={community.links.logo.replace("/logo", community.slug)}>
              {" "}
              {community.metadata.title}
            </a>
            {isCommunityRestricted && (
              <span
                class="ui label horizontal small access-status restricted rel-ml-1"
                title={i18next.t("Community visibility")}
                data-tooltip={i18next.t(
                  "The community is restricted to users with access."
                )}
                data-inverted=""
              >
                <i class="icon ban" aria-hidden="true"></i>{" "}
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
