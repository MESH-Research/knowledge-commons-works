/*
* This file is part of Knowledge Commons Works.
*   Copyright (C) 2024 Mesh Research.
*
* Knowledge Commons Works is based on InvenioRDM, and
* this file is based on code from InvenioRDM. InvenioRDM is
*   Copyright (C) 2020-2024 CERN.
*   Copyright (C) 2020-2024 Northwestern University.
*   Copyright (C) 2020-2024 T U Wien.
*
* InvenioRDM and Knowledge Commons Works are both free software;
* you can redistribute and/or modify them under the terms of the
* MIT License; see LICENSE file for more details.
*/

import {
  SearchAppFacets,
  SearchAppResultsPane,
} from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_requests/i18next";
import { RequestStatusFilter } from "./RequestStatusFilterComponent";
import PropTypes from "prop-types";
import React from "react";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import { SearchBar } from "react-searchkit";
import { Button, Container, Grid } from "semantic-ui-react";

export const RequestsSearchLayout = ({ config, appName }) => {
  const [sidebarVisible, setSidebarVisible] = React.useState(false);
  return (
    <Container>
      <Grid>
        <Grid.Row>
          <Grid.Column only="mobile tablet" mobile={3} tablet={1}>
            <Button
              basic
              size="medium"
              icon="sliders"
              onClick={() => setSidebarVisible(true)}
              aria-label={i18next.t("Filter results")}
              className="rel-mb-1"
            />
          </Grid.Column>

          <Grid.Column
            mobile={13}
            tablet={5}
            computer={4}
            className="text-align-right-mobile"
          >
            <RequestStatusFilter className="rel-mb-1" />
          </Grid.Column>

          <Grid.Column mobile={16} tablet={10} computer={8}>
            <SearchBar placeholder={i18next.t("Search in my requests...")} />
          </Grid.Column>

        </Grid.Row>

        <Grid.Row>
          <Grid.Column mobile={16} tablet={16} computer={12}>
            <SearchAppResultsPane
              layoutOptions={config.layoutOptions}
              appName={appName}
            />
          </Grid.Column>
          <GridResponsiveSidebarColumn
            width={4}
            open={sidebarVisible}
            onHideClick={() => setSidebarVisible(false)}
            className="widescreen large monitor only"
          >
            <SearchAppFacets aggs={config.aggs} appName={appName} />
          </GridResponsiveSidebarColumn>
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
