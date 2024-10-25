/*
 * This file is part of Invenio.
 * Copyright (C) 2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import PropTypes from "prop-types";
import React from "react";
import Overridable from "react-overridable";
import {
  buildUID,
} from "react-searchkit";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import { Card, Container, Grid, List } from "semantic-ui-react";
import { i18next } from "@translations/invenio_search_ui/i18next";
import _isEmpty from "lodash/isEmpty";
import {
  // SearchAppFacets,
  SearchAppResultsPane,
  // SearchBar,
} from "@js/invenio_search_ui/components";
import { ContribSearchAppFacets } from "@js/invenio_search_ui/components";
import {
    ResultOptionsWithState,
} from "./ResultOptions";
import { RecordSearchBarElement } from "./RecordSearchBarElement";

const ContribSearchHelpLinks = (props) => {
  const { appName="" } = props;
  return (
    <Overridable id={buildUID("SearchHelpLinks", "", appName)}>
      <List>
        <List.Item>
          <a href="/help/search">{i18next.t("Advanced search guide")}</a>
        </List.Item>
      </List>
    </Overridable>
  );
};

ContribSearchHelpLinks.propTypes = {
  appName: PropTypes.string,
};


const SearchAppLayout = ({ config, appName, help=true, toggle=true }) => {

  const [sidebarVisible, setSidebarVisible] = React.useState(false);
  const facetsAvailable = !_isEmpty(config.aggs);

  const resultsPaneLayoutNoFacets = { width: 16 };

  const resultsPaneLayoutFacets = {
    mobile: 16,
    tablet: 16,
    computer: 11,
    largeScreen: 11,
    widescreen: 11,
    width: undefined,
  };

  // make list full width if no facets available
  const resultsPaneLayout = facetsAvailable
    ? resultsPaneLayoutFacets
    : resultsPaneLayoutNoFacets;

  const columnsAmount = facetsAvailable ? 2 : 1;

  return (
    <Container fluid>
        <Grid>
          <Overridable
            id={buildUID("SearchApp.searchbarContainer", "", appName)}
          >
              <Grid.Row className="pb-0 pt-0">
                <Grid.Column
                  mobile={16}
                  tablet={16}
                  computer={11}
                  largeScreen={11}
                  widescreen={11}
                >
                  <RecordSearchBarElement buildUID={buildUID} appName={appName} />
                </Grid.Column>
                <Grid.Column
                  mobile={4}
                  tablet={4}
                  computer={5}
                  largeScreen={5}
                  widescreen={5}
                >
                </Grid.Column>
              </Grid.Row>
          </Overridable>

        <ResultOptionsWithState
          appName={appName}
          facetsAvailable={facetsAvailable}
          sortOptions={config.sortOptions}
          layoutOptions={config.layoutOptions}
          setSidebarVisible={setSidebarVisible}
        />

        <Grid.Row columns={columnsAmount}>

          {/* results list */}
          <Grid.Column
            as="section"
            className="search-results-pane"
            aria-label={i18next.t("Search results")}
            {...resultsPaneLayout}
          >
            <SearchAppResultsPane
              layoutOptions={config.layoutOptions} appName={appName} buildUID={buildUID}
            />
            {/* <div class="ui fluid placeholder rel-mt-3">
              <div class="header">
                <div class="line"></div>
              </div>

              <div class="paragraph">
                <div class="line"></div>
              </div>

              <div class="paragraph">
                <div class="line"></div>
                <div class="line"></div>
              </div>

              <div class="paragraph">
                <div class="line"></div>
              </div>
            </div> */}

          </Grid.Column>

          {/* computer facets sidebar */}
          {facetsAvailable && (
            <GridResponsiveSidebarColumn
              ariaLabel={i18next.t("Search filters")}
              mobile={4}
              tablet={4}
              computer={5}
              largeScreen={5}
              widescreen={5}
              open={sidebarVisible}
              onHideClick={() => setSidebarVisible(false)}
            >
              <h2 className="ui header mobile tablet only">Search Help and Filters</h2>
              {help && (
                <Card className="borderless facet mt-0">
                  <Card.Content>
                    <Card.Header as="h2">{i18next.t("Help")}</Card.Header>
                    <ContribSearchHelpLinks appName={appName}/>
                  </Card.Content>
                </Card>
              )}
              <ContribSearchAppFacets aggs={config.aggs} appName={appName} buildUID={buildUID} help={false} toggle={toggle} />
            </GridResponsiveSidebarColumn>
          )}

        </Grid.Row>
      </Grid>
    </Container>
  );
}

SearchAppLayout.propTypes = {
  config: PropTypes.object.isRequired,
  appName: PropTypes.string.isRequired,
  help: PropTypes.bool,
  toggle: PropTypes.bool,
};

export { SearchAppLayout };