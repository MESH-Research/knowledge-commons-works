import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Icon, Image, Grid } from "semantic-ui-react";

const CommunitiesBanner = ({ community, isPreviewSubmissionRequest, show }) => {
  console.log("****CommunitiesBanner community", community);
  const isCommunityRestricted = community
    ? community.access.visibility == "restricted"
    : false;
  return (
    !isPreviewSubmissionRequest &&
    community && (
      <div
        id="communities"
        className={`sidebar-container ${show}`}
        aria-label={i18next.t("Record communities")}
      >
        <div className="ui container segment rdm-sidebar pr-0">
          <Grid verticalAlign="middle">
            <Grid.Row>
              <Grid.Column width={12}>
                <h3 className="ui header small">
                  <a href={`/communities/${community.slug}`}>
                    {community.metadata.title}
                  </a>
                </h3>
                {isCommunityRestricted && (
                  <div
                    className="ui label horizontal small access-status restricted rel-ml-1"
                    title={i18next.t("Community visibility")}
                    data-tooltip={i18next.t(
                      "The community is restricted to users with access."
                    )}
                    data-inverted=""
                  >
                    <i className="icon ban" aria-hidden="true"></i>{" "}
                    {i18next.t("Restricted")}
                  </div>
                )}
              </Grid.Column>
              <Grid.Column width={4}>
                <object data={community.links.logo} type="image/png">
                  <Icon name="group" size="large" />
                </object>
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </div>
      </div>
    )
  );
};

export { CommunitiesBanner };
