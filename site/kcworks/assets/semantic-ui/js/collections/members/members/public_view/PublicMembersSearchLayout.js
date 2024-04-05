/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_communities/i18next";
import React, { Component } from "react";
import { SearchBar } from "react-searchkit";
import { Grid } from "semantic-ui-react";
import PropTypes from "prop-types";

const PublicViewSearchBar = () => {
  return (
    <Grid>
      <Grid.Row columns={2}>
        <Grid.Column width={16}>
          <SearchBar placeholder={i18next.t("Search members...")} />
        </Grid.Column>
      </Grid.Row>
    </Grid>
  );
};

export class PublicMembersSearchLayout extends Component {
  render() {
    const { config, appName } = this.props;
    return (
      <>
        <PublicViewSearchBar />
        <SearchAppResultsPane layoutOptions={config.layoutOptions} appName={appName} />
      </>
    );
  }
}

PublicMembersSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  appName: PropTypes.string,
};

PublicMembersSearchLayout.defaultProps = {
  appName: "",
};
