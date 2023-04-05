/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { parametrize, overrideStore } from "react-overridable";
import {
  LabelTypeSubmission,
  LabelTypeInvitation,
  LabelStatusSubmit,
  LabelStatusDelete,
  LabelStatusAccept,
  LabelStatusDecline,
  LabelStatusCancel,
  LabelStatusExpire,
} from "@js/invenio_requests/request";
import {
  RecordSearchBarElement,
  RequestsEmptyResultsWithState,
  RequestsResults,
  RequestsResultsGridItemTemplate,
  RequestsResultsItemTemplateCommunity,
  RequestsSearchLayout,
} from "./requests";
import {
  RequestAcceptModalTrigger,
  RequestCancelModalTrigger,
  RequestDeclineModalTrigger,
} from "@js/invenio_requests/components/ModalTriggers";
import {
  RequestAcceptButton,
  RequestCancelButton,
  RequestDeclineButton,
} from "@js/invenio_requests/components/Buttons";
import {
  ContribSearchAppFacets,
  ContribBucketAggregationElement,
  ContribBucketAggregationValuesElement,
} from "@js/invenio_search_ui/components";

const domContainer = document.getElementById("communities-request-search-root");

const appName = "InvenioCommunities.RequestSearch";

const community = JSON.parse(domContainer.dataset.community);

const RequestsResultsGridItemTemplateWithCommunity = parametrize(
  RequestsResultsGridItemTemplate,
  {
    community: community,
  }
);

const RequestsResultsItemTemplateWithCommunity = parametrize(
  RequestsResultsItemTemplateCommunity,
  {
    community: community,
  }
);
const RequestAcceptModalTriggerWithConfig = parametrize(RequestAcceptModalTrigger, {
  size: "mini",
  className: "ml-5",
});

const RequestDeclineModalTriggerWithConfig = parametrize(RequestDeclineModalTrigger, {
  size: "mini",
  className: "ml-5",
});

const RequestCancelModalTriggerWithConfig = parametrize(RequestCancelModalTrigger, {
  size: "mini",
  className: "ml-5",
});

const RequestsSearchLayoutWAppName = parametrize(RequestsSearchLayout, {
  appName: appName,
});

const CommunitySubmission = () => (
  <LabelTypeSubmission className="primary" size="small" />
);

const CommunityInvitation = () => (
  <LabelTypeInvitation className="primary" size="small" />
);

const Submitted = () => <LabelStatusSubmit className="primary" size="small" />;

const Deleted = () => <LabelStatusDelete className="negative" size="small" />;

const Accepted = () => <LabelStatusAccept className="positive" size="small" />;

const Declined = () => <LabelStatusDecline className="negative" size="small" />;

const Cancelled = () => <LabelStatusCancel className="neutral" size="small" />;

const Expired = () => <LabelStatusExpire className="expired" size="small" />;

const defaultComponents = {
  [`${appName}.BucketAggregation.element`]: ContribBucketAggregationElement,
  [`${appName}.BucketAggregationValues.element`]: ContribBucketAggregationValuesElement,
  [`${appName}.SearchApp.facets`]: ContribSearchAppFacets,
  [`${appName}.ResultsList.item`]: RequestsResultsItemTemplateWithCommunity,
  [`${appName}.ResultsGrid.item`]: RequestsResultsGridItemTemplateWithCommunity,
  [`${appName}.SearchApp.layout`]: RequestsSearchLayoutWAppName,
  [`${appName}.SearchApp.results`]: RequestsResults,
  [`${appName}.SearchBar.element`]: RecordSearchBarElement,
  [`${appName}.EmptyResults.element`]: RequestsEmptyResultsWithState,
  [`RequestTypeLabel.layout.community-submission`]: CommunitySubmission,
  [`RequestTypeLabel.layout.community-invitation`]: CommunityInvitation,
  [`RequestStatusLabel.layout.submitted`]: Submitted,
  [`RequestStatusLabel.layout.deleted`]: Deleted,
  [`RequestStatusLabel.layout.accepted`]: Accepted,
  [`RequestStatusLabel.layout.declined`]: Declined,
  [`RequestStatusLabel.layout.cancelled`]: Cancelled,
  [`RequestStatusLabel.layout.expired`]: Expired,
  [`RequestActionModalTrigger.accept`]: RequestAcceptModalTriggerWithConfig,
  [`RequestActionModalTrigger.decline`]: RequestDeclineModalTriggerWithConfig,
  [`RequestActionModalTrigger.cancel`]: RequestCancelModalTriggerWithConfig,
  [`RequestActionButton.cancel`]: RequestCancelButton,
  [`RequestActionButton.decline`]: RequestDeclineButton,
  [`RequestActionButton.accept`]: RequestAcceptButton,
};

const overriddenComponents = overrideStore.getAll();

// Auto-initialize search app
createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true
);
