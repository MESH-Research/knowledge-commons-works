/*
 * This file is part of Invenio.
 * Copyright (C) 2022-2023 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { defaultContribComponents } from "@js/invenio_requests/contrib";
import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  ContribBucketAggregationElement,
  ContribBucketAggregationValuesElement,
  ContribSearchAppFacets,
} from "@js/invenio_search_ui/components";
import { overrideStore, parametrize } from "react-overridable";
import {
  RecordSearchBarElement,
  RequestsResultsItemTemplateCommunity,
} from "./requests";
import {
  RequestsSearchLayout,
  RequestsEmptyResultsWithState,
  RequestsResults,
} from "@js/invenio_requests/search";

const domContainer = document.getElementById("communities-request-search-root");

const appName = "InvenioCommunities.RequestSearch";

const community = JSON.parse(domContainer.dataset.community);

const RequestsResultsItemTemplateWithCommunity = parametrize(
  RequestsResultsItemTemplateCommunity,
  {
    community: community,
  }
);

const RequestsSearchLayoutWAppName = parametrize(RequestsSearchLayout, {
  appName: appName,
});

const defaultComponents = {
  [`${appName}.BucketAggregation.element`]: ContribBucketAggregationElement,
  [`${appName}.BucketAggregationValues.element`]: ContribBucketAggregationValuesElement,
  [`${appName}.SearchApp.facets`]: ContribSearchAppFacets,
  [`${appName}.ResultsList.item`]: RequestsResultsItemTemplateWithCommunity,
  [`${appName}.ResultsGrid.item`]: () => null,
  [`${appName}.SearchApp.layout`]: RequestsSearchLayoutWAppName,
  [`${appName}.SearchApp.results`]: RequestsResults,
  [`${appName}.SearchBar.element`]: RecordSearchBarElement,
  [`${appName}.EmptyResults.element`]: RequestsEmptyResultsWithState,
  ...defaultContribComponents,
};

const overriddenComponents = overrideStore.getAll();

// Auto-initialize search app
createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true
);
