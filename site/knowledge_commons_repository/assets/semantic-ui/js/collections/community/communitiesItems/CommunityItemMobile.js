// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import { CommunityTypeLabel } from "../labels";
import { RestrictedLabel } from "../labels";
import React from "react";
import { Image } from "react-invenio-forms";
import { Button, Grid, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";

export const CommunityItemMobile = ({ result, index }) => {
  const communityType = result.ui?.type?.title_l10n;
  const canUpdate = result.ui.permissions.can_update;
  return (
    <Grid className="mobile only item community-item">
      {result.access.visibility === "restricted" && (
        <Grid.Row>
          <Grid.Column width={16} verticalAlign="middle" className="pl-0 pr-0">
            <RestrictedLabel access={result.access.visibility} />
          </Grid.Column>
        </Grid.Row>
      )}

      <Grid.Row>
        <Grid.Column
          width={(canUpdate && 11) || 16}
          verticalAlign="middle"
          className="pl-0 pr-0"
        >
          <div className="flex align-items-center">
            <Image
              wrapped
              src={result.links.logo}
              size="mini"
              className="community-image rel-mr-1"
              alt=""
            />
            <div>
              <a
                className="truncate-lines-2 ui medium header m-0"
                href={result.links.self_html}
              >
                {result.metadata.title}
              </a>
            </div>
          </div>
        </Grid.Column>

        {canUpdate && (
          <Grid.Column
            width={5}
            verticalAlign="middle"
            textAlign="right"
            className="pr-0"
          >
            <Button
              compact
              size="tiny"
              href={result.links.settings_html}
              className="mt-0 mr-0"
              labelPosition="left"
              icon="edit"
              content={i18next.t("Edit")}
            />
          </Grid.Column>
        )}
      </Grid.Row>

      {result.metadata.description && (
        <Grid.Row className="pt-0">
          <Grid.Column width={16} className="pl-0 pr-0">
            <p className="truncate-lines-1 text size small text-muted mt-5">
              {result.metadata.description}
            </p>
          </Grid.Column>
        </Grid.Row>
      )}

      {(communityType || result.metadata.website || result.metadata.organizations) && (
        <Grid.Row className="pt-0">
          <Grid.Column width={16} verticalAlign="bottom" className="pl-0 pr-0">
            <div className="text size small text-muted">
              {communityType && (
                <div className="mb-5">
                  <CommunityTypeLabel transparent type={communityType} />
                </div>
              )}

              {result.metadata.website && (
                <div className="rel-mr-1 mb-5">
                  <Icon name="linkify" />
                  <a
                    href={result.metadata.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted"
                  >
                    {result.metadata.website}
                  </a>
                </div>
              )}

              {result.metadata.organizations && (
                <div className="mb-5">
                  <Icon name="building outline" />
                  {result.metadata.organizations.map((org, index) => {
                    const separator = (index > 0 && ", ") || "";

                    return (
                      <span className="text-muted" key={org.name}>
                        {separator}
                        {org.name}
                        {org.id && (
                          <a
                            href={`https://ror.org/${org.id}`}
                            aria-label={`${org.name}'s ROR ${i18next.t("profile")}`}
                            title={`${org.name}'s ROR ${i18next.t("profile")}`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            <img
                              className="inline-id-icon ml-5"
                              src="/static/images/ror-icon.svg"
                              alt=""
                            />
                          </a>
                        )}
                      </span>
                    );
                  })}
                </div>
              )}
            </div>
          </Grid.Column>
        </Grid.Row>
      )}
    </Grid>
  );
};

CommunityItemMobile.propTypes = {
  result: PropTypes.object.isRequired,
  index: PropTypes.string,
};

CommunityItemMobile.defaultProps = {
  index: null,
};
