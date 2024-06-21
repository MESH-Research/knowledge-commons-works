/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
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

const appName = "InvenioCommunities.Search";

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

// Auto-initialize search app
createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true
);
