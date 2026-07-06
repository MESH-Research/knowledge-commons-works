/*
 * Based on a file in Invenio Communities
 * Copyright (C) 2024 CERN.
 *
 * Modifications for Knowledge Commons Works
 * Copyright (C) 2026 Mesh Research
 *
 * Invenio and Knowledge Commons Works are both free software; you
 * can redistribute and/or modify them under the terms of the MIT License;
 * see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  ContribBucketAggregationElement,
  ContribBucketAggregationValuesElement,
  ContribSearchAppFacets,
} from "@js/invenio_search_ui/components";
import { overrideStore, parametrize } from "react-overridable";
import {
  CommunitiesResults,
  CommunitiesSearchBarElement,
  CommunitiesSearchLayout,
  CommunityItem,
  ResultsGridItemTemplate,
} from "./";

const appName = "InvenioSubCommunities.Search";

const ContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  help: false,
});

const CommunitiesSearchLayoutConfig = parametrize(CommunitiesSearchLayout, {
  appName: appName,
});

export const defaultComponents = {
  [`${appName}.BucketAggregation.element`]: ContribBucketAggregationElement,
  [`${appName}.BucketAggregationValues.element`]: ContribBucketAggregationValuesElement,
  [`${appName}.SearchApp.facets`]: ContribSearchAppFacetsWithConfig,
  [`${appName}.ResultsList.item`]: CommunityItem,
  [`${appName}.ResultsGrid.item`]: ResultsGridItemTemplate,
  [`${appName}.SearchApp.layout`]: CommunitiesSearchLayoutConfig,
  [`${appName}.SearchBar.element`]: CommunitiesSearchBarElement,
  [`${appName}.SearchApp.results`]: CommunitiesResults,
};

const overriddenComponents = overrideStore.getAll();

createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true
);
