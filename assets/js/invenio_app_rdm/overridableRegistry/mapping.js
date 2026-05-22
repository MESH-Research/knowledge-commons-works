// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { parametrize } from "react-overridable";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/i18next";

// import { AccessRightField } from "./fields/AccessRightField";
import { ContribSearchAppFacets } from "@js/invenio_search_ui/components/common/facets";
import { CommunityPrivilegesFormLayout } from "./collections/settings/privileges/CommunityPrivilegesFormLayout";
import { CurationPolicyFormLayout } from "./collections/settings/curation_policy/CurationPolicyFormLayout";
import { DangerZone } from "./collections/settings/profile/DangerZone";
import { InvitationResultItemWithConfig } from "./collections/invitations/InvitationResultItemWithConfig";
import { LogoUploader } from "./collections/settings/profile/LogoUploader";
import { ManagerMembersResultItemWithConfig } from "./collections/members/manager_view/ManagerMembersResultItem";
import { MembersEmptyResults } from "./collections/members/components/MembersEmptyResults";
import { MembersSearchBarElement } from "./collections/members/components/MembersSearchBarElement";
import Pagination from "./search/Pagination";
// import { InvenioSearchPagination } from "./search/InvenioSearchPagination";
import ResultsPerPage from "./search/ResultsPerPage";
import { PublicMembersResultsItemWithCommunity } from "./collections/members/public_view/PublicMembersResultItem";
import { RDMRecordMultipleSearchBarElement } from "./search/RDMRecordMultipleSearchBarElement";
import RecordsResultsListItem from "./search/RecordsResultsListItem";
import { RecordResultsListItemDashboard } from "./search/RecordsResultsListItemDashboard";
import { RecordSearchBarElement } from "./search/RecordSearchBarElement";
import { RequestMetadata } from "./requests/RequestMetadata";
import { RequestsResultsItemTemplateDashboard } from "./user_dashboard/RequestsResultsItemTemplateDashboard";
import { RequestsResultsItemTemplateWithCommunity } from "./collections/members/requests/RequestsResultsItemTemplate";
import { RequestsSearchLayout } from "./requests/search/RequestsSearchLayout";
// import { RelatedWorksField } from "./fields/RelatedWorksField";
import { KcworksSubmitReviewModal } from "./deposit/SubmitReviewModal";
import { RequestActions } from "./requests/actions/RequestActions";
import { ResultOptionsWithState } from "./search/ResultOptions";
import { Results } from "./search/Results";
import { SearchAppLayout } from "./search/SearchAppLayout";
import { SubjectsField } from "./fields/SubjectsField";
import { TitlesField } from "./fields/TitlesField";

const MobileActionMenu = () => {
  return (
    <div className="col-12">
      <h1>HERE IT IS</h1>
    </div>
  );
};

const DashboardSearchBarElementWithConfig = parametrize(RecordSearchBarElement, {
  placeholder: "Search my works...",
});

const SearchAppLayoutWithConfig = parametrize(SearchAppLayout, {
  appName: "InvenioAppRdm.Search",
});

const DashboardRequestsSearchLayoutWithApp = parametrize(RequestsSearchLayout, {
  appName: "InvenioAppRdm.DashboardRequests",
});

const CommunityRequestsSearchLayoutWithApp = parametrize(RequestsSearchLayout, {
  appName: "InvenioCommunities.RequestSearch",
});

const ContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  toggle: true,
  help: true,
});

export const DashboardUploadsSearchLayout = parametrize(SearchAppLayout, {
  searchBarPlaceholder: i18next.t("Search in my works..."),
  newBtn: (
    <Button
      positive
      icon="upload"
      href="/uploads/new"
      content={i18next.t("New upload")}
      floated="right"
    />
  ),
  appName: "InvenioAppRdm.DashboardUploads",
});

export const overriddenComponents = {
  "InvenioAppRdm.DashboardRequests.SearchApp.layout": DashboardRequestsSearchLayoutWithApp,
  "InvenioAppRdm.DashboardRequests.ResultsList.item": RequestsResultsItemTemplateDashboard,
  "InvenioAppRdm.DashboardUploads.SearchApp.layout": DashboardUploadsSearchLayout,
  "InvenioAppRdm.DashboardUploads.SearchBar.element": DashboardSearchBarElementWithConfig,
  "InvenioAppRdm.DashboardUploads.ResultsList.item": RecordResultsListItemDashboard,
  // "InvenioAppRdm.Deposit.AccessRightField.container": AccessRightField,
  // "InvenioAppRdm.Deposit.RelatedWorksField.container": RelatedWorksField,
  "InvenioAppRdm.Deposit.SubjectsField.container": SubjectsField,
  "InvenioAppRdm.Deposit.TitlesField.container": TitlesField,
  "InvenioAppRdm.RecordsList.RecordsResultsListItem.layout": RecordsResultsListItem,
  "InvenioAppRDM.RecordsList.RecordsResultsListItem.layout": RecordsResultsListItem,
  "InvenioAppRdm.Search.RecordsResultsListItem.layout": RecordsResultsListItem,
  "InvenioAppRdm.Search.SearchBar.element": RDMRecordMultipleSearchBarElement,
  "InvenioAppRdm.Search.SearchApp.facets": ContribSearchAppFacetsWithConfig,
  "InvenioAppRdm.Search.SearchApp.layout": SearchAppLayoutWithConfig,
  "InvenioAppRdm.Search.SearchApp.pagination": Pagination,
  Pagination: Pagination,
  "InvenioAppRdm.Search.ResultsPerPage": ResultsPerPage,
  ResultsPerPage: ResultsPerPage,
  "InvenioAppRdm.Search.SearchApp.results": Results,
  "InvenioAppRdm.Search.SearchApp.resultOptions": ResultOptionsWithState,
  // "InvenioCommunities.CommunityPrivilegesForm.layout": CommunityPrivilegesFormLayout,
  // "InvenioCommunities.CurationPolicyForm.layout": CurationPolicyFormLayout,
  // "InvenioCommunities.CommunityProfileForm.GridRow.DangerZone": DangerZone,  // trans only
  // "InvenioCommunities.CommunityProfileForm.LogoUploader.ProfilePicture": LogoUploader,  // fix now upstream
  "InvenioCommunities.DetailsSearch.ResultsList.item": RecordsResultsListItem,
  "InvenioCommunities.DetailsSearch.SearchApp.results": Results,
  // "InvenioCommunities.DetailsSearch.pagination": Pagination,
  "InvenioCommunities.RequestSearch.ResultsList.item": RequestsResultsItemTemplateWithCommunity,
  "InvenioCommunities.RequestSearch.SearchApp.layout": CommunityRequestsSearchLayoutWithApp,
  "InvenioCommunities.InvitationsSearch.ResultsList.item": InvitationResultItemWithConfig,
  // "InvenioCommunities.ManagerSearch.EmptyResults.element": MembersEmptyResults,  // trans only
  // "InvenioCommunities.ManagerSearch.ResultsList.item": ManagerMembersResultItemWithConfig,
  // "InvenioCommunities.ManagerSearch.SearchBar.element": MembersSearchBarElement,
  // "InvenioCommunities.MemberSearch.ResultsList.item": ManagerMembersResultItemWithConfig,
  // "InvenioCommunities.MemberSearch.EmptyResults.element": MembersEmptyResults,
  // "InvenioCommunities.MemberSearch.SearchBar.element": MembersSearchBarElement,
  // "InvenioCommunities.PublicSearch.ResultsList.item": PublicMembersResultsItemWithCommunity,
  // "InvenioCommunities.PublicSearch.SearchBar.element": MembersSearchBarElement,
  // "InvenioCommunities.PublicSearch.EmptyResults.element": MembersEmptyResults,  // trans only
  "InvenioModularDetailPage.MobileActionMenu.container": MobileActionMenu,
  // InvenioCommunities.Search.SearchApp.layout: CommunityRecordsSearchAppLayout,
  "InvenioRdmRecords.SubmitReviewModal.container": KcworksSubmitReviewModal,
  "InvenioRequests.RequestActions.layout": RequestActions,
  "InvenioRequest.RequestMetadata.Layout": RequestMetadata,
};
