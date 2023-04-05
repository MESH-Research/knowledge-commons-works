// This file is part of Invenio
// Copyright (C) 2022 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it under the
// terms of the MIT License; see LICENSE file for more details.

import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  CommunityCountComponent,
  CommunityEmptyResults,
  CommunityErrorComponent,
  CommunityRecordResultsGridItem,
  CommunityRecordResultsListItem,
  CommunityRecordSearchAppLayout,
  CommunityRecordSearchBarElement,
  CommunityToggleComponent,
} from "./components";
import { parametrize, overrideStore } from "react-overridable";
import {
  ContribSearchAppFacets,
  ContribBucketAggregationElement,
  ContribBucketAggregationValuesElement,
} from "@js/invenio_search_ui/components";

const appName = "InvenioCommunities.DetailsSearch";

const ContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  toogle: true,
});

const CommunityRecordSearchAppLayoutWAppName = parametrize(
  CommunityRecordSearchAppLayout,
  {
    appName: appName,
  }
);

const defaultComponents = {
  [`${appName}.BucketAggregation.element`]: ContribBucketAggregationElement,
  [`${appName}.BucketAggregationValues.element`]: ContribBucketAggregationValuesElement,
  [`${appName}.ResultsGrid.item`]: CommunityRecordResultsGridItem,
  [`${appName}.EmptyResults.element`]: CommunityEmptyResults,
  [`${appName}.ResultsList.item`]: CommunityRecordResultsListItem,
  [`${appName}.SearchApp.facets`]: ContribSearchAppFacetsWithConfig,
  [`${appName}.SearchApp.layout`]: CommunityRecordSearchAppLayoutWAppName,
  [`${appName}.SearchBar.element`]: CommunityRecordSearchBarElement,
  [`${appName}.Count.element`]: CommunityCountComponent,
  [`${appName}.Error.element`]: CommunityErrorComponent,
  [`${appName}.SearchFilters.Toggle.element`]: CommunityToggleComponent,
};

const overriddenComponents = overrideStore.getAll();

createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true
);
