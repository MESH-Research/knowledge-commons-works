/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { InvitationsContextProvider } from "../../api/invitations/InvitationsContextProvider";
import { RequestStatusFilter } from "../../requests/requests";
import { Filters } from "../Filters";
import { InvitationsMembersModalWithSearchKit } from "./invitationsModal/InvitationsMembersModal";
import { SearchBar, Sort } from "react-searchkit";
import { FilterLabels } from "../components/FilterLabels";
import { SearchFilters } from "@js/invenio_search_ui/components/SearchFilters";

export class InvitationsSearchLayout extends Component {
  render() {
    const {
      config,
      roles,
      rolesCanInvite,
      community,
      communityGroupsEnabled,
      appName,
    } = this.props;

    const filtersClass = new Filters(roles);
    const customFilters = filtersClass.getInvitationFilters();

    return (
      <>
        {/* auto column grid used instead of SUI grid for better searchbar width adjustment */}
        <div className="auto-column-grid">
          <div className="flex">
            <RequestStatusFilter keepFiltersOnUpdate />
            <SearchBar fluid />
          </div>
          <div>
            <SearchFilters customFilters={customFilters} />
            <Sort values={config.sortOptions} />
            <InvitationsContextProvider community={community}>
              <InvitationsMembersModalWithSearchKit
                rolesCanInvite={rolesCanInvite}
                groupsEnabled={communityGroupsEnabled}
                community={community}
              />
            </InvitationsContextProvider>
          </div>
        </div>

        <div className="rel-mb-1">
          <FilterLabels ignoreFilters={["is_open"]} />
        </div>

        <SearchAppResultsPane layoutOptions={config.layoutOptions} appName={appName} />
      </>
    );
  }
}

InvitationsSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  roles: PropTypes.array.isRequired,
  rolesCanInvite: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  communityGroupsEnabled: PropTypes.bool.isRequired,
  appName: PropTypes.string,
};

InvitationsSearchLayout.defaultProps = {
  appName: "",
};
