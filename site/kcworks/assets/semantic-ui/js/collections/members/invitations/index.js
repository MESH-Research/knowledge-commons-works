/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";
import { parametrize, overrideStore } from "react-overridable";
import { DropdownSort } from "@js/invenio_search_ui/components";
import { InvitationsContextProvider as ContextProvider } from "../../api/invitations/InvitationsContextProvider";
import { InvitationResultItem } from "./InvitationResultItem";
import { InvitationsResults } from "./InvitationsResults";
import { InvitationsResultsContainer } from "./InvitationsResultsContainer";
import { InvitationsSearchBarElement } from "./InvitationsSearchBarElement";
import { InvitationsSearchLayout } from "./InvitationsSearchLayout";
import { InvitationsEmptyResults } from "./InvitationsEmptyResults";
import {
  SubmitStatus,
  DeleteStatus,
  AcceptStatus,
  DeclineStatus,
  CancelStatus,
  ExpireStatus,
} from "@js/invenio_requests/request";

const dataAttr = document.getElementById("community-invitations-search-root").dataset;
const community = JSON.parse(dataAttr.community);
const communitiesAllRoles = JSON.parse(dataAttr.communitiesAllRoles);
const communitiesRolesCanInvite = JSON.parse(dataAttr.communitiesRolesCanInvite);
const permissions = JSON.parse(dataAttr.permissions);

const appName = "InvenioCommunities.InvitationsSearch";

const communityGroupsEnabled = JSON.parse(dataAttr.communityGroupsEnabled);

const InvitationResultItemWithConfig = parametrize(InvitationResultItem, {
  config: { rolesCanInvite: communitiesRolesCanInvite },
  community: community,
});

const InvitationsSearchLayoutWithConfig = parametrize(InvitationsSearchLayout, {
  roles: communitiesAllRoles,
  rolesCanInvite: communitiesRolesCanInvite,
  community: community,
  permissions: permissions,
  communityGroupsEnabled: communityGroupsEnabled,
  appName: appName,
});

const InvitationsContextProvider = parametrize(ContextProvider, {
  community: community,
});

const InvitationsResultsContainerWithConfig = parametrize(InvitationsResultsContainer, {
  rolesCanInvite: communitiesRolesCanInvite,
  community: community,
  communityGroupsEnabled: communityGroupsEnabled,
});

const InvitationsEmptyResultsWithCommunity = parametrize(InvitationsEmptyResults, {
  community: community,
  communityGroupsEnabled: communityGroupsEnabled,
  rolesCanInvite: communitiesRolesCanInvite,
});

const defaultComponents = {
  [`${appName}.EmptyResults.element`]: InvitationsEmptyResultsWithCommunity,
  [`${appName}.ResultsList.item`]: InvitationResultItemWithConfig,
  [`${appName}.SearchApp.layout`]: InvitationsSearchLayoutWithConfig,
  [`${appName}.SearchBar.element`]: InvitationsSearchBarElement,
  [`${appName}.SearchApp.results`]: InvitationsResults,
  [`${appName}.ResultsList.container`]: InvitationsResultsContainerWithConfig,
  [`${appName}.Sort.element`]: DropdownSort,
  [`RequestStatus.layout.submitted`]: SubmitStatus,
  [`RequestStatus.layout.deleted`]: DeleteStatus,
  [`RequestStatus.layout.accepted`]: AcceptStatus,
  [`RequestStatus.layout.declined`]: DeclineStatus,
  [`RequestStatus.layout.cancelled`]: CancelStatus,
  [`RequestStatus.layout.expired`]: ExpireStatus,
};

const overriddenComponents = overrideStore.getAll();

// Auto-initialize search app
createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true,
  InvitationsContextProvider
);
