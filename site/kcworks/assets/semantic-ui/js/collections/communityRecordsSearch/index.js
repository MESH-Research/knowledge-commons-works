// This file is part of Invenio
// Copyright (C) 2022 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it under the
// terms of the MIT License; see LICENSE file for more details.

import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  RDMCountComponent,
  RDMEmptyResults,
  RDMErrorComponent,
  RDMRecordResultsGridItem,
  RDMToggleComponent,
} from "@js/invenio_app_rdm/search/components";
import RecordsResultsListItem from "@js/invenio_app_rdm/components/RecordsResultsListItem";
import {
  CommunityRecordsSearchAppLayout,
  CommunityRecordsSearchBarElement,
  CommunityRecordsSearchEmptyResults,
} from "./components";
import { parametrize, overrideStore } from "react-overridable";
import {
  ContribSearchAppFacets,
  ContribBucketAggregationElement,
  ContribBucketAggregationValuesElement,
} from "@js/invenio_search_ui/components";

const appName = "InvenioCommunities.DetailsSearch";

const ContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  toggle: true,
});

const CommunityRecordSearchAppLayoutWAppName = parametrize(
  CommunityRecordsSearchAppLayout,
  {
    appName: appName,
  }
);

const defaultComponents = {
  [`${appName}.BucketAggregation.element`]: ContribBucketAggregationElement,
  [`${appName}.BucketAggregationValues.element`]: ContribBucketAggregationValuesElement,
  [`${appName}.ResultsGrid.item`]: RDMRecordResultsGridItem,
  [`${appName}.EmptyResults.element`]: CommunityRecordsSearchEmptyResults,
  [`${appName}.ResultsList.item`]: RecordsResultsListItem,
  [`${appName}.SearchApp.facets`]: ContribSearchAppFacetsWithConfig,
  [`${appName}.SearchApp.layout`]: CommunityRecordSearchAppLayoutWAppName,
  [`${appName}.SearchBar.element`]: CommunityRecordsSearchBarElement,
  [`${appName}.Count.element`]: RDMCountComponent,
  [`${appName}.Error.element`]: RDMErrorComponent,
  [`${appName}.SearchFilters.Toggle.element`]: RDMToggleComponent,
};

const overriddenComponents = overrideStore.getAll();

createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true
);
