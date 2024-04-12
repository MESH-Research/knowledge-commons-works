/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";
import { DropdownSort } from "@js/invenio_search_ui/components";
import { overrideStore, parametrize } from "react-overridable";

import { PublicMembersResultsItem } from "./PublicMembersResultItem";
import { MembersSearchBarElement } from "../../components/MembersSearchBarElement";
import { MembersResults } from "../components/MembersResult";
import { MembersResultsGridItem } from "../components/MembersResultsGridItem";
import { PublicMembersResultsContainer } from "./PublicMembersResultContainer";
import { PublicMembersSearchLayout } from "./PublicMembersSearchLayout";
import MembersEmptyResults from "../components/MembersEmptyResults";

const appName = "InvenioCommunities.PublicSearch";

const PublicMembersSearchLayoutWithConfig = parametrize(PublicMembersSearchLayout, {
  appName: appName,
});

const defaultComponents = {
  [`${appName}.ResultsList.item`]: PublicMembersResultsItem,
  [`${appName}.ResultsGrid.item`]: MembersResultsGridItem,
  [`${appName}.SearchApp.layout`]: PublicMembersSearchLayoutWithConfig,
  [`${appName}.SearchBar.element`]: MembersSearchBarElement,
  [`${appName}.SearchApp.results`]: MembersResults,
  [`${appName}.ResultsList.container`]: PublicMembersResultsContainer,
  [`${appName}.EmptyResults.element`]: MembersEmptyResults,
  [`${appName}.Sort.element`]: DropdownSort,
};

const overriddenComponents = overrideStore.getAll();

// Auto-initialize search app
createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true
);
