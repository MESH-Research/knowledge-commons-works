/*
 * This file is part of Invenio.
 * Copyright (C) 2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import PropTypes from "prop-types";
import React from "react";
import Overridable, {
  OverridableContext,
  overrideStore,
} from "react-overridable";
import {
  InvenioSearchApi,
  ReactSearchKit,
  withState,
  buildUID,
} from "react-searchkit";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import { Container, Grid, Button } from "semantic-ui-react";
import { ResultOptions } from "./Results";
import { SearchBar } from "./SearchBar";
import { SearchConfigurationContext } from "./context";
import { i18next } from "@translations/invenio_search_ui/i18next";
import _isEmpty from "lodash/isEmpty";
import { SearchAppFacets } from "./SearchAppFacets";
import { SearchAppResultsPane } from "./SearchAppResultsPane";

const ResultOptionsWithState = withState(ResultOptions);

export const SearchApp = ({ config, appName }) => {
  const [sidebarVisible, setSidebarVisible] = React.useState(false);
  const searchApi = new InvenioSearchApi(config.searchApi);
  const context = {
    appName,
    buildUID: (element) => buildUID(element, "", appName),
    ...config,
  };
  const facetsAvailable = !_isEmpty(config.aggs);

  const resultsPaneLayoutNoFacets = { width: 16 };
  const resultsSortLayoutNoFacets = { width: 16 };

  const resultsPaneLayoutFacets = {
    mobile: 16,
    tablet: 16,
    computer: 12,
    largeScreen: 13,
    widescreen: 13,
    width: undefined,
  };

  const resultsSortLayoutFacets = {
    mobile: 14,
    tablet: 15,
    computer: 12,
    largeScreen: 13,
    widescreen: 13,
  };

  // make list full width if no facets available
  const resultsPaneLayout = facetsAvailable
    ? resultsPaneLayoutFacets
    : resultsPaneLayoutNoFacets;

  const resultSortLayout = facetsAvailable
    ? resultsSortLayoutFacets
    : resultsSortLayoutNoFacets;

  const columnsAmount = facetsAvailable ? 2 : 1;

  return (
    <OverridableContext.Provider value={overrideStore.getAll()}>
      <SearchConfigurationContext.Provider value={context}>
        <ReactSearchKit
          searchApi={searchApi}
          appName={appName}
          initialQueryState={config.initialQueryState}
          defaultSortingOnEmptyQueryString={
            config.defaultSortingOnEmptyQueryString
          }
        >
          <Overridable
            id={buildUID("SearchApp.layout", "", appName)}
            config={config}
          >
            <Container fluid>
              <Overridable
                id={buildUID("SearchApp.searchbarContainer", "", appName)}
              >
                <Grid relaxed padded>
                  <Grid.Row>
                    <Grid.Column width={12} floated="right">
                      <SearchBar buildUID={buildUID} appName={appName}/>
                    </Grid.Column>
                  </Grid.Row>
                </Grid>
              </Overridable>

              <Grid relaxed>
                <Grid.Row
                  textAlign="right"
                  columns={columnsAmount}
                  className="result-options rel-mt-2"
                >
                  {facetsAvailable && (
                    <Grid.Column
                      only="mobile tablet"
                      mobile={2}
                      tablet={1}
                      textAlign="center"
                      verticalAlign="middle"
                    >
                      <Button
                        basic
                        icon="sliders"
                        onClick={() => setSidebarVisible(true)}
                        aria-label={i18next.t("Filter results")}
                      />
                    </Grid.Column>
                  )}

                  <Grid.Column {...resultSortLayout} floated="right">
                    <ResultOptionsWithState
                      sortOptions={config.sortOptions}
                      layoutOptions={config.layoutOptions}
                    />
                  </Grid.Column>
                </Grid.Row>

                <Grid.Row columns={columnsAmount}>
                  {facetsAvailable && (
                    <GridResponsiveSidebarColumn
                      mobile={4}
                      tablet={4}
                      computer={4}
                      largeScreen={3}
                      widescreen={3}
                      open={sidebarVisible}
                      onHideClick={() => setSidebarVisible(false)}
                    >
                      <SearchAppFacets aggs={config.aggs} appName={appName} buildUID={buildUID}/>
                    </GridResponsiveSidebarColumn>
                  )}

                  <Grid.Column {...resultsPaneLayout}>
                    <SearchAppResultsPane
                      layoutOptions={config.layoutOptions} appName={appName} buildUID={buildUID}
                    />
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Container>
          </Overridable>
        </ReactSearchKit>
      </SearchConfigurationContext.Provider>
    </OverridableContext.Provider>
  );
};

SearchApp.propTypes = {
  config: PropTypes.shape({
    searchApi: PropTypes.object.isRequired, // same as ReactSearchKit.searchApi
    initialQueryState: PropTypes.shape({
      queryString: PropTypes.string,
      sortBy: PropTypes.string,
      sortOrder: PropTypes.string,
      page: PropTypes.number,
      size: PropTypes.number,
      hiddenParams: PropTypes.array,
      layout: PropTypes.oneOf(["list", "grid"]),
    }),
    aggs: PropTypes.arrayOf(
      PropTypes.shape({
        title: PropTypes.string,
        aggName: PropTypes.string,
        access_right: PropTypes.string,
        mapping: PropTypes.object,
      })
    ),
    sortOptions: PropTypes.arrayOf(
      PropTypes.shape({
        sortBy: PropTypes.string,
        sortOrder: PropTypes.string,
        text: PropTypes.string,
      })
    ),
    paginationOptions: PropTypes.shape({
      resultsPerPage: PropTypes.arrayOf(
        PropTypes.shape({
          text: PropTypes.string,
          value: PropTypes.number,
        })
      ),
    }),
    layoutOptions: PropTypes.shape({
      listView: PropTypes.bool.isRequired,
      gridView: PropTypes.bool.isRequired,
    }).isRequired,
    defaultSortingOnEmptyQueryString: PropTypes.shape({
      sortBy: PropTypes.string,
      sortOrder: PropTypes.string,
    }),
  }).isRequired,
  appName: PropTypes.string,
};

SearchApp.defaultProps = {
  config: {
    searchApi: {
      url: "",
      withCredentials: false,
      headers: {},
    },
    initialQueryState: {},
    aggs: [],
    sortOptions: [],
    paginationOptions: {},
    layoutOptions: {
      listView: true,
      gridView: false,
    },
    defaultSortingOnEmptyQueryString: {},
  },
  appName: null,
};
