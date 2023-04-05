// This file is part of Invenio
// Copyright (C) 2022 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  SearchAppFacets,
  SearchAppResultsPane,
  InvenioSearchPagination,
} from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import { Count, ResultsList, SearchBar, Sort, withState } from "react-searchkit";
import {
  Button,
  Card,
  Container,
  Grid,
  Header,
  Icon,
  Input,
  Segment,
} from "semantic-ui-react";
import { ComputerTabletRequestsItem } from "./requests_items/ComputerTabletRequestsItem";
import { MobileRequestsItem } from "./requests_items/MobileRequestsItem";

export const RecordSearchBarElement = withState(
  ({
    placeholder: passedPlaceholder,
    queryString,
    onInputChange,
    updateQueryState,
    currentQueryState,
  }) => {
    const placeholder = passedPlaceholder || i18next.t("Search");

    const onSearch = () => {
      updateQueryState({ ...currentQueryState, queryString });
    };

    const onBtnSearchClick = () => {
      onSearch();
    };
    const onKeyPress = (event) => {
      if (event.key === "Enter") {
        onSearch();
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

export const RequestsResults = ({
  sortOptions,
  paginationOptions,
  currentResultsState,
}) => {
  const { total } = currentResultsState.data;
  return (
    total && (
      <Grid>
        <Grid.Row>
          <Grid.Column width={16}>
            <Segment>
              <Grid>
                <Grid.Row
                  verticalAlign="middle"
                  className="small pt-5 pb-5 highlight-background"
                >
                  <Grid.Column width={4}>
                    <Count
                      label={() => (
                        <>
                          {i18next.t("{{total}} result(s) found", {
                            total: total,
                          })}
                        </>
                      )}
                    />
                  </Grid.Column>
                  <Grid.Column width={12} textAlign="right">
                    {sortOptions && (
                      <Sort
                        values={sortOptions}
                        label={(cmp) => (
                          <>
                            <label className="mr-10">{i18next.t("Sort by")}</label>
                            {cmp}
                          </>
                        )}
                      />
                    )}
                  </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                  <Grid.Column>
                    <ResultsList />
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Segment>
          </Grid.Column>
        </Grid.Row>
        <InvenioSearchPagination paginationOptions={paginationOptions} />
      </Grid>
    )
  );
};

RequestsResults.propTypes = {
  sortOptions: PropTypes.object.isRequired,
  paginationOptions: PropTypes.object.isRequired,
  currentResultsState: PropTypes.object.isRequired,
};

export const RequestsResultsGridItemTemplate = ({ result, community }) => {
  return (
    <Card fluid href={`/communities/${community.slug}/requests/${result.id}`}>
      <Card.Content>
        <Card.Header>{result.metadata.title}</Card.Header>
        <Card.Description>
          <div dangerouslySetInnerHTML={{ __html: result.metadata.description }} />
        </Card.Description>
      </Card.Content>
    </Card>
  );
};

RequestsResultsGridItemTemplate.propTypes = {
  result: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
};

export const RequestsResultsItemTemplateCommunity = ({ result, community }) => {
  const ComputerTabletRequestsItemWithState = withState(ComputerTabletRequestsItem);
  const MobileRequestsItemWithState = withState(MobileRequestsItem);
  return (
    <>
      <ComputerTabletRequestsItemWithState result={result} community={community} />
      <MobileRequestsItemWithState result={result} community={community} />
    </>
  );
};

RequestsResultsItemTemplateCommunity.propTypes = {
  result: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
};

class RequestStatusFilterComponent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      open: undefined,
    };
  }

  componentDidMount() {
    const { currentQueryState } = this.props;
    const userSelectionFilters = currentQueryState.filters;
    const openFilter = userSelectionFilters.find((obj) => obj.includes("is_open"));
    if (openFilter) {
      // eslint-disable-next-line react/no-did-mount-set-state
      this.setState({
        open: openFilter.includes("true"),
      });
    }
  }

  /**
   * Updates queryFilters based on selection and removing previous filters
   * @param {string} OpenStatus true if open requests and false if closed requests
   */
  retrieveRequests = (OpenStatus) => {
    const { currentQueryState, updateQueryState, keepFiltersOnUpdate } = this.props;
    const { open } = this.state;

    if (open === OpenStatus) {
      return;
    }
    this.setState({
      open: OpenStatus,
    });
    currentQueryState.filters = keepFiltersOnUpdate
      ? currentQueryState.filters.filter((element) => element[0] !== "is_open")
      : [];
    currentQueryState.filters.push(["is_open", OpenStatus]);
    updateQueryState(currentQueryState);
  };

  retrieveOpenRequests = () => {
    this.retrieveRequests(true);
  };

  retrieveClosedRequests = () => {
    this.retrieveRequests(false);
  };

  render() {
    const { open } = this.state;
    return (
      <Button.Group basic>
        <Button
          className="request-search-filter"
          onClick={this.retrieveOpenRequests}
          active={open === true}
        >
          {i18next.t("Open")}
        </Button>
        <Button
          className="request-search-filter"
          onClick={this.retrieveClosedRequests}
          active={open === false}
        >
          {i18next.t("Closed")}
        </Button>
      </Button.Group>
    );
  }
}

RequestStatusFilterComponent.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  keepFiltersOnUpdate: PropTypes.bool,
};

RequestStatusFilterComponent.defaultProps = {
  keepFiltersOnUpdate: false,
};

export const RequestStatusFilter = withState(RequestStatusFilterComponent);

export const RequestsSearchLayout = (props) => {
  const [sidebarVisible, setSidebarVisible] = React.useState(false);
  const { config, appName } = props;
  return (
    <Container>
      <Grid>
        <Grid.Row>
          <Grid.Column
            only="mobile tablet"
            mobile={2}
            tablet={1}
            verticalAlign="middle"
            className="rel-mb-1"
          >
            <Button
              basic
              icon="sliders"
              onClick={() => setSidebarVisible(true)}
              aria-label={i18next.t("Filter results")}
            />
          </Grid.Column>
          <Grid.Column
            mobile={14}
            tablet={6}
            computer={3}
            floated="right"
            className="text-align-right-mobile"
          >
            <RequestStatusFilter />
          </Grid.Column>
          <Grid.Column mobile={16} tablet={9} computer={9} className="rel-mb-1">
            <SearchBar placeholder={i18next.t("Search requests...")} />
          </Grid.Column>
        </Grid.Row>
        <Grid.Row columns={2}>
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

RequestsSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  appName: PropTypes.string,
};

RequestsSearchLayout.defaultProps = {
  appName: undefined,
};

export const RequestsEmptyResults = ({
  queryString,
  userSelectionFilters,
  updateQueryState,
}) => {
  const isOpen = userSelectionFilters.some(
    (obj) => obj.includes("is_open") && obj.includes("true")
  );
  const filtersToNotReset = userSelectionFilters.find((obj) => obj.includes("is_open"));
  const elementsToReset = {
    queryString: "",
    page: 1,
    filters: [filtersToNotReset],
  };

  const AllDone = () => {
    return (
      <Header as="h1" icon>
        {i18next.t("All done!")}
        <Header.Subheader>
          {i18next.t("You've caught up with all open requests.")}
        </Header.Subheader>
      </Header>
    );
  };

  const NoResults = () => {
    return (
      <>
        <Header icon>
          <Icon name="search" />
          {i18next.t("No requests found!")}
        </Header>
        {queryString && (
          <Button primary onClick={() => updateQueryState(elementsToReset)}>
            {i18next.t("Reset search")}
          </Button>
        )}
      </>
    );
  };

  const allRequestsDone = isOpen && !queryString;
  return (
    <Segment placeholder textAlign="center">
      {allRequestsDone ? <AllDone /> : <NoResults />}
    </Segment>
  );
};

RequestsEmptyResults.propTypes = {
  queryString: PropTypes.string.isRequired,
  userSelectionFilters: PropTypes.array.isRequired,
  updateQueryState: PropTypes.func.isRequired,
};

export const RequestsEmptyResultsWithState = withState(RequestsEmptyResults);
