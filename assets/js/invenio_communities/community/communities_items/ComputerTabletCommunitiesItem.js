// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_communities/i18next";
import React from "react";
import { Image } from "react-invenio-forms";
import { Icon, Item, Label, Grid } from "semantic-ui-react";
import { DateTime } from "luxon";
import PropTypes from "prop-types";

export const ComputerTabletCommunitiesItem = ({ result }) => {
  const communityType = result.ui?.type?.title_l10n;
  const visibility = result.access.visibility;
  const isPublic = visibility === "public";
  const visibilityColor = isPublic ? "green" : "red";
  const visibilityText = isPublic ? i18next.t("Public") : i18next.t("Restricted");
  const visibilityIcon = isPublic ? undefined : "ban";
  return (
    <Item key={result.id} className="computer tablet only flex community-item">
      <Image
        wrapped
        src={result.links.logo}
        size="tiny"
        className="community-logo rel-mt-1"
      />
      <Item.Content>
        <Grid>
          <Grid.Row>
            <Grid.Column width={13}>
              <Item.Extra className="user-communities">
                {communityType && (
                  <Label size="tiny" color="blue">
                    <Icon name="tag" />
                    {communityType}
                  </Label>
                )}
                <Label size="tiny" color={visibilityColor}>
                  {visibilityIcon && <Icon name={visibilityIcon} />}
                  {visibilityText}
                </Label>
              </Item.Extra>
              <Item.Header as="h2">
                <a href={`/communities/${result.id}`}>{result.metadata.title}</a>
              </Item.Header>
              <Item.Meta>
                <div
                  className="truncate-lines-2"
                  dangerouslySetInnerHTML={{
                    __html: result.metadata.description,
                  }}
                />
              </Item.Meta>
              <Item>
                {result.metadata.website && (
                  <a
                    href={result.metadata.website}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {result.metadata.website}
                  </a>
                )}
              </Item>
            </Grid.Column>
            <Grid.Column width={3} className="flex column">
              <Item.Extra className="text-align-right mt-auto">
                {i18next.t("Created: ")}
                {DateTime.fromISO(result.created).toLocaleString(i18next.language)}
              </Item.Extra>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Item.Content>
    </Item>
  );
};

ComputerTabletCommunitiesItem.propTypes = {
  result: PropTypes.object.isRequired,
};
