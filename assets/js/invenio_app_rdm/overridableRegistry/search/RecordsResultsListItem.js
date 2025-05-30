// This file is part of InvenioRDM
// Copyright (C) 2022-2024 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/i18next";
import _get from "lodash/get";
import _truncate from "lodash/truncate";
import React, { Component } from "react";
// import Overridable from "react-overridable";
import { SearchItemCreators } from "@js/invenio_app_rdm/utils";
import PropTypes from "prop-types";
import { Item, Grid, Icon, Label } from "semantic-ui-react";
// import { buildUID } from "react-searchkit";
import { CompactStats } from "./records_list_item_components/CompactStats";
// import { DisplayVerifiedCommunity } from "./records_list_item_components/DisplayVerifiedCommunity";
import { DisplayPartOfCommunities } from "./records_list_item_components/DisplayPartOfCommunities";

class RecordsResultsListItem extends Component {
  render() {
    const { currentQueryState, result, key, appName } = this.props;

    const accessStatusId = _get(result, "ui.access_status.id", "open");
    const accessStatus = _get(result, "ui.access_status.title_l10n", "Open");
    const accessStatusIcon = _get(result, "ui.access_status.icon", "unlock");
    const createdDate = _get(
      result,
      "ui.created_date_l10n_long",
      "No creation date found."
    );

    const creators = result.ui.creators.creators;

    const descriptionStripped = _get(
      result,
      "ui.description_stripped",
      "No description"
    );

    const publicationDate = _get(
      result,
      "ui.publication_date_l10n_long",
      "No publication date found."
    );
    const resourceType = _get(
      result,
      "ui.resource_type.title_l10n",
      "No resource type"
    );
    const subjects = _get(result, "ui.subjects", []);
    const title = _get(result, "metadata.title", "No title");
    const version = _get(result, "ui.version", null);
    const versions = _get(result, "versions");
    const uniqueViews = _get(result, "stats.all_versions.unique_views", 0);
    const uniqueDownloads = _get(result, "stats.all_versions.unique_downloads", 0);

    const publishingInformation = _get(result, "ui.publishing_information.journal", "");

    const filters = currentQueryState && Object.fromEntries(currentQueryState.filters);
    const allVersionsVisible = filters?.allversions;
    const numOtherVersions = versions.index - 1;

    // Derivatives
    const viewLink = `/records/${result.id}`;
    return (
        <Item className="search-result" key={key ?? result.id}>
          <Item.Content>
            {/* FIXME: Uncomment to enable themed banner */}
            {/* <DisplayVerifiedCommunity communities={result.parent?.communities} /> */}
            <Item.Header as="h2">
              <a href={viewLink}>{title}</a>
            </Item.Header>
            <Item className="creatibutors">
              <Icon name={`${creators.length === 1 ? "user" : "users"}`} /> <SearchItemCreators creators={creators} othersLink={viewLink} />
            </Item>
            <Item.Description>
              {_truncate(descriptionStripped, { length: 350 })}
            </Item.Description>
            <Item.Extra className="item-footer ui grid">
              <Grid.Column mobile={16} tablet={11} computer={11} className="item-footer-left">
                {subjects.map((subject) => (
                  <Label key={subject.title_l10n} size="tiny">
                    {subject.title_l10n}
                  </Label>
                ))}
                  <p>
                    <Label horizontal size="small" className="">
                      {publicationDate} ({version})
                    </Label>
                    <Label horizontal size="small" className="">
                      {resourceType}
                    </Label>
                    <Label
                      horizontal
                      size="small"
                      className={`basic access-status ${accessStatusId}`}
                    >
                      {accessStatusIcon && <Icon name={accessStatusIcon} />}
                      {accessStatus}
                    </Label>
                    {/* {createdDate && publishingInformation && " | "} */}
                  </p>

                    {publishingInformation && (
                      <p>
                        {i18next.t("Published in: {{publishInfo}}", {
                          publishInfo: publishingInformation,
                        })}
                      </p>
                    )}

                  {!allVersionsVisible && versions.index > 1 && (
                    <p>
                      <b>
                        {i18next.t("{{count}} more versions exist for this record", {
                          count: numOtherVersions,
                        })}
                      </b>
                    </p>
                  )}

                  <DisplayPartOfCommunities communities={result.parent?.communities} />
              </Grid.Column>

              <Grid.Column mobile={16} tablet={5} computer={5} className="item-footer-right">
                <small>
                  <CompactStats
                    uniqueViews={uniqueViews}
                    uniqueDownloads={uniqueDownloads}
                  />
                </small>
                {createdDate && (
                  <small className="created-date">
                    {i18next.t("Uploaded on {{uploadDate}}", {
                      uploadDate: createdDate,
                    })}
                  </small>
                )}
              </Grid.Column>
            </Item.Extra>
          </Item.Content>
        </Item>
    );
  }
}

RecordsResultsListItem.propTypes = {
  currentQueryState: PropTypes.object,
  result: PropTypes.object.isRequired,
  key: PropTypes.string,
  appName: PropTypes.string,
};

RecordsResultsListItem.defaultProps = {
  key: null,
  currentQueryState: null,
  appName: "",
};

export default RecordsResultsListItem;
