/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import { Filters } from "../../Filters";
import { FilterLabels } from "../../components/FilterLabels";
import { SearchFilters } from "@js/invenio_search_ui/components";
import { SearchBar, Sort } from "react-searchkit";
import PropTypes from "prop-types";

export class MembersSearchLayout extends Component {
  render() {
    const { config, roles, appName } = this.props;
    const filtersClass = new Filters(roles);
    const customFilters = filtersClass.getMembersFilters();
    return (
      <>
        {/* auto column grid used instead of SUI grid for better searchbar width adjustment */}
        <div className="auto-column-grid">
          <div>
            <SearchBar fluid />
          </div>
          <div>
            <SearchFilters customFilters={customFilters} />
            <Sort values={config.sortOptions} />
          </div>
        </div>

        <div className="rel-mb-1">
          <FilterLabels />
        </div>

        <SearchAppResultsPane layoutOptions={config.layoutOptions} appName={appName} />
      </>
    );
  }
}

MembersSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  roles: PropTypes.array.isRequired,
  appName: PropTypes.string,
};

MembersSearchLayout.defaultProps = {
  appName: "",
};
