// This file is part of Invenio
// Copyright (C) 2022 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it under the
// terms of the MIT License; see LICENSE file for more details.

import {
  SearchAppFacets,
  SearchAppResultsPane,
  SearchBar,
  MultipleOptionsSearchBarRSK,
} from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_communities/i18next";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import _truncate from "lodash/truncate";
import React from "react";
import { withState, Count, Sort } from "react-searchkit";
import {
  Button,
  Card,
  Checkbox,
  Container,
  Grid,
  Header,
  Icon,
  Input,
  Item,
  Label,
  Message,
  Segment,
} from "semantic-ui-react";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import PropTypes from "prop-types";

export const CommunityRecordResultsListItem = ({ result }) => {
  const accessStatusId = _get(result, "ui.access_status.id", "open");
  const accessStatus = _get(result, "ui.access_status.title_l10n", "Open");
  const accessStatusIcon = _get(result, "ui.access_status.icon", "unlock");
  const createdDate = _get(
    result,
    "ui.created_date_l10n_long",
    "No creation date found."
  );
  const creators = result.ui.creators.creators.slice(0, 3);

  const descriptionStripped = _get(result, "ui.description_stripped", "No description");

  const publicationDate = _get(
    result,
    "ui.publication_date_l10n_long",
    "No publication date found."
  );
  const resourceType = _get(result, "ui.resource_type.title_l10n", "No resource type");
  const subjects = _get(result, "ui.subjects", []);
  const title = _get(result, "metadata.title", "No title");
  const version = _get(result, "ui.version", null);

  // Derivatives
  const viewLink = `/records/${result.id}`;
  return (
    <Item>
      <Item.Content>
        <Item.Extra className="labels-actions">
          <Label size="tiny" className="primary">
            {publicationDate} ({version})
          </Label>
          <Label size="tiny" className="neutral">
            {resourceType}
          </Label>
          <Label size="tiny" className={`access-status ${accessStatusId}`}>
            {accessStatusIcon && <i className={`icon ${accessStatusIcon}`} />}
            {accessStatus}
          </Label>
        </Item.Extra>
        <Item.Header as="h2">
          <a href={viewLink}>{title}</a>
        </Item.Header>
        <Item className="creatibutors">
          <SearchItemCreators creators={creators} />
        </Item>
        <Item.Description>
          {_truncate(descriptionStripped, { length: 350 })}
        </Item.Description>
        <Item.Extra>
          {subjects.map((subject) => (
            <Label key={subject.id} size="tiny">
              {subject.title_l10n}
            </Label>
          ))}
          {createdDate && (
            <div>
              <small>
                {i18next.t("Uploaded on")} <span>{createdDate}</span>
              </small>
            </div>
          )}
        </Item.Extra>
      </Item.Content>
    </Item>
  );
};

CommunityRecordResultsListItem.propTypes = {
  result: PropTypes.object.isRequired,
};

// TODO: Update this according to the full List item template?
export const CommunityRecordResultsGridItem = ({ result }) => {
  const descriptionStripped = _get(result, "ui.description_stripped", "No description");
  return (
    <Card fluid href={`/records/${result.pid}`}>
      <Card.Content>
        <Card.Header>{result.metadata.title}</Card.Header>
        <Card.Description>
          {_truncate(descriptionStripped, { length: 200 })}
        </Card.Description>
      </Card.Content>
    </Card>
  );
};

CommunityRecordResultsGridItem.propTypes = {
  result: PropTypes.object.isRequired,
};

export const CommunityRecordSearchAppLayout = ({ config, appName }) => {
  const [sidebarVisible, setSidebarVisible] = React.useState(false);

  return (
    <Container className="rel-pt-2">
      <Grid>
        <Grid.Column only="mobile tablet" mobile={2} tablet={1}>
          <Button
            basic
            icon="sliders"
            onClick={() => setSidebarVisible(true)}
            aria-label={i18next.t("Filter results")}
          />
        </Grid.Column>

        <Grid.Column mobile={14} tablet={14} computer={12} floated="right">
          <Grid>
            <Grid.Column width={16}>
              <SearchBar placeholder={i18next.t("Search records in community...")} />
            </Grid.Column>

            <Grid.Column width={4} textAlign="left">
              <Count
                label={(cmp) => (
                  <>
                    {cmp} {i18next.t("result(s) found")}
                  </>
                )}
              />
            </Grid.Column>
            <Grid.Column width={12} textAlign="right">
              <Sort
                values={config.sortOptions}
                label={(cmp) => (
                  <>
                    <label className="mr-10">{i18next.t("Sort by")}</label>
                    {cmp}
                  </>
                )}
              />
            </Grid.Column>
          </Grid>
        </Grid.Column>

        <Grid.Row>
          <GridResponsiveSidebarColumn
            width={4}
            open={sidebarVisible}
            onHideClick={() => setSidebarVisible(false)}
            // eslint-disable-next-line react/no-children-prop
            children={<SearchAppFacets aggs={config.aggs} appName={appName} />}
          />
          <Grid.Column mobile={16} tablet={16} computer={12}>
            <SearchAppResultsPane
              layoutOptions={config.layoutOptions}
              appName={appName}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Container>
  );
};

CommunityRecordSearchAppLayout.propTypes = {
  config: PropTypes.object.isRequired,
  appName: PropTypes.string,
};

CommunityRecordSearchAppLayout.defaultProps = {
  appName: "",
};

export const CommunityRecordSingleSearchBarElement = withState(
  ({
    placeholder: passedPlaceholder,
    queryString,
    onInputChange,
    updateQueryState,
  }) => {
    const placeholder = passedPlaceholder || i18next.t("Search");
    const onBtnSearchClick = () => {
      updateQueryState({ queryString, filters: [] });
    };
    const onKeyPress = (event) => {
      if (event.key === "Enter") {
        updateQueryState({ queryString, filters: [] });
      }
    };
    return (
      <Input
        action={{
          "icon": "search",
          "onClick": onBtnSearchClick,
          "className": "search",
          "aria-label": i18next.t("Search"),
        }}
        fluid
        placeholder={placeholder}
        onChange={(event, { value }) => {
          onInputChange(value);
        }}
        value={queryString}
        onKeyPress={onKeyPress}
      />
    );
  }
);

export const CommunityRecordSearchBarElement = ({ queryString, onInputChange }) => {
  const headerSearchbar = document.getElementById("header-search-bar");
  const searchbarOptions = headerSearchbar.dataset.options
    ? JSON.parse(headerSearchbar.dataset.options)
    : [];

  if (!_isEmpty(searchbarOptions)) {
    return (
      <MultipleOptionsSearchBarRSK
        options={searchbarOptions}
        onInputChange={onInputChange}
        queryString={queryString}
        placeholder={i18next.t("Search records...")}
      />
    );
  } else {
    // backwards compatibility
    return (
      <CommunityRecordSingleSearchBarElement
        placeholder={i18next.t("Search records...")}
        queryString={queryString}
        onInputChange={onInputChange}
      />
    );
  }
};

CommunityRecordSearchBarElement.propTypes = {
  queryString: PropTypes.string.isRequired,
  onInputChange: PropTypes.func.isRequired,
};

export const CommunityToggleComponent = ({
  updateQueryFilters,
  userSelectionFilters,
  filterValue,
  label,
  title,
}) => {
  const _isChecked = (userSelectionFilters) => {
    const isFilterActive =
      userSelectionFilters.filter((filter) => filter[0] === filterValue[0]).length > 0;
    return isFilterActive;
  };

  const onToggleClicked = () => {
    updateQueryFilters(filterValue);
  };

  const isFilterChecked = _isChecked(userSelectionFilters);
  return (
    <Card className="borderless facet">
      <Card.Content>
        <Card.Header as="h2">{title}</Card.Header>
      </Card.Content>
      <Card.Content>
        <Checkbox
          toggle
          label={label}
          name="versions-toggle"
          id="versions-toggle"
          onClick={onToggleClicked}
          checked={isFilterChecked}
        />
      </Card.Content>
    </Card>
  );
};

CommunityToggleComponent.propTypes = {
  updateQueryFilters: PropTypes.func.isRequired,
  userSelectionFilters: PropTypes.array.isRequired,
  filterValue: PropTypes.array.isRequired,
  label: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
};

export const CommunityCountComponent = ({ totalResults }) => {
  return <Label>{totalResults.toLocaleString("en-US")}</Label>;
};

CommunityCountComponent.propTypes = {
  totalResults: PropTypes.number.isRequired,
};

export const CommunityEmptyResults = (props) => {
  const { queryString, searchPath, resetQuery } = props;

  return (
    <Grid>
      <Grid.Row centered>
        <Grid.Column width={12} textAlign="center">
          <Header as="h2">
            {i18next.t("We couldn't find any matches for ")}
            {(queryString && `'${queryString}'`) || i18next.t("your search")}
          </Header>
        </Grid.Column>
      </Grid.Row>
      <Grid.Row centered>
        <Grid.Column width={8} textAlign="center">
          <Button primary onClick={resetQuery}>
            <Icon name="search" />
            {i18next.t("Start over")}
          </Button>
        </Grid.Column>
      </Grid.Row>
      <Grid.Row centered>
        <Grid.Column width={12}>
          <Segment secondary padded size="large">
            <Header as="h3" size="small">
              {i18next.t("ProTip")}!
            </Header>
            <p>
              <a href={`${searchPath}?q=metadata.publication_date:[2017-01-01 TO *]`}>
                metadata.publication_date:[2017-01-01 TO *]
              </a>{" "}
              {i18next.t("will give you all the publications from 2017 until today")}.
            </p>
            <p>
              {i18next.t("For more tips, check out our ")}
              <a href="/help/search" title={i18next.t("Search guide")}>
                {i18next.t("search guide")}
              </a>
              {i18next.t(" for defining advanced search queries")}.
            </p>
          </Segment>
        </Grid.Column>
      </Grid.Row>
    </Grid>
  );
};

CommunityEmptyResults.propTypes = {
  queryString: PropTypes.string.isRequired,
  resetQuery: PropTypes.func.isRequired,
  searchPath: PropTypes.string,
};

CommunityEmptyResults.defaultProps = {
  searchPath: "/search",
};

export const CommunityErrorComponent = ({ error }) => {
  return (
    <Message warning>
      <Message.Header>
        <Icon name="warning sign" />
        {error.response.data.message}
      </Message.Header>
    </Message>
  );
};

CommunityErrorComponent.propTypes = {
  error: PropTypes.object.isRequired,
};

export function SearchItemCreators({ creators }) {
  function getIcon(creator) {
    let ids = _get(creator, "person_or_org.identifiers", []);
    let creatorName = _get(creator, "person_or_org.name", "No name");
    let firstId = ids.filter((id) => ["orcid", "ror"].includes(id.scheme))[0];
    firstId = firstId || { scheme: "" };
    let icon = null;
    switch (firstId.scheme) {
      case "orcid":
        icon = (
          <a
            className="identifier-link"
            href={`https://orcid.org/${firstId.identifier}`}
            aria-label={`${creatorName}: ${i18next.t("ORCID profile")}`}
            title={`${creatorName}: ${i18next.t("ORCID profile")}`}
          >
            <img className="inline-id-icon" src="/static/images/orcid.svg" alt="" />
          </a>
        );
        break;
      case "ror":
        icon = (
          <a
            href={`https://ror.org/${firstId.identifier}`}
            aria-label={`${creatorName}: ${i18next.t("ROR profile")}`}
            title={`${creatorName}: ${i18next.t("ROR profile")}`}
          >
            <img className="inline-id-icon" src="/static/images/ror-icon.svg" alt="" />
          </a>
        );
        break;
      default:
        break;
    }
    return icon;
  }

  function getLink(creator) {
    let creatorName = _get(creator, "person_or_org.name", "No name");
    let link = (
      <a
        className="creatibutor-link"
        href={`/search?q=metadata.creators.person_or_org.name:"${creatorName}"`}
        title={`${creatorName}: ${i18next.t("Search")}`}
      >
        <span className="creatibutor-name">{creatorName}</span>
      </a>
    );
    return link;
  }

  return creators.map((creator, index) => (
    <span
      className="creatibutor-wrap"
      key={creator.person_or_org?.identifiers?.identifier}
    >
      {getLink(creator)}
      {getIcon(creator)}
      {index < creators.length - 1 && ";"}
    </span>
  ));
}
