/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import { Filters } from "../../Filters";
import { FilterLabels } from "../../components/FilterLabels";
import { SearchFilters } from "@js/invenio_search_ui/components";
import { SearchBar, Sort } from "react-searchkit";
import { InvitationsContextProvider } from "../../../api/invitations/InvitationsContextProvider";
import { InvitationsMembersModalWithSearchKit } from "../../invitations/invitationsModal/InvitationsMembersModal";

export class ManagerSearchLayout extends Component {
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
    const customFilters = filtersClass.getMembersFilters();
    return (
      <>
        {/* auto column grid used instead of SUI grid for better searchbar width adjustment */}
        <div className="auto-column-grid">
          <div>
            <div className="mobile only rel-mb-1">
              <InvitationsContextProvider community={community}>
                <InvitationsMembersModalWithSearchKit
                  rolesCanInvite={rolesCanInvite}
                  groupsEnabled={communityGroupsEnabled}
                  community={community}
                />
              </InvitationsContextProvider>
            </div>
            <SearchBar fluid />
          </div>

          <div className="flex align-items-center column-mobile">
            <div className="tablet only">
              <InvitationsContextProvider community={community}>
                <InvitationsMembersModalWithSearchKit
                  rolesCanInvite={rolesCanInvite}
                  groupsEnabled={communityGroupsEnabled}
                  community={community}
                />
              </InvitationsContextProvider>
            </div>

            <div className="full-width flex align-items-center justify-end column-mobile">
              <SearchFilters customFilters={customFilters} />
              <Sort values={config.sortOptions} />
            </div>
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

ManagerSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  roles: PropTypes.array.isRequired,
  rolesCanInvite: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  communityGroupsEnabled: PropTypes.bool.isRequired,
  appName: PropTypes.string,
};

ManagerSearchLayout.defaultProps = {
  appName: "",
};
