// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { parametrize } from "react-overridable";

import { AccessRightField } from "./fields/AccessRightField";
import { CreatibutorsField } from "./fields/CreatibutorsField";
import { CommunityPrivilegesFormLayout } from "./collections/settings/privileges/CommunityPrivilegesFormLayout";
import { CurationPolicyFormLayout } from "./collections/settings/curation_policy/CurationPolicyFormLayout";
import { DangerZone } from "./collections/settings/profile/DangerZone";
import { DescriptionsField } from "./fields/DescriptionsField";
import { FormFeedback } from "./fields/FormFeedback";
import { FundingField } from "./fields/FundingField";
import { IdentifiersField } from "./fields/IdentifiersField";
import { InvitationResultItemWithConfig } from "./collections/invitations/InvitationResultItemWithConfig";
import { LicenseField } from "./fields/LicenseField";
import { LogoUploader } from "./collections/settings/profile/LogoUploader";
import { ManagerMembersResultItemWithConfig } from "./collections/members/manager_view/ManagerMembersResultItem";
import { MembersSearchBarElement } from "./collections/members/components/MembersSearchBarElement";
import { MetadataOnlyToggle } from "./fields/MetadataOnlyToggle";
import { PublicationDateField } from "./fields/PublicationDateField";
import { PublicMembersResultsItemWithCommunity } from "./collections/members/public_view/PublicMembersResultItem";
import { PublisherField } from "./fields/PublisherField";
import RecordsResultsListItem from "./search/RecordsResultsListItem";
import { RequestMetadata } from "./requests/RequestMetadata";
import { RequestsResultsItemTemplateDashboard } from "./user_dashboard/RequestsResultsItemTemplateDashboard";
import { RequestsResultsItemTemplateWithCommunity } from "./collections/members/requests/RequestsResultsItemTemplate";
import { RequestsSearchLayout } from "./requests/search/RequestsSearchLayout";
import { RDMRecordMultipleSearchBarElement } from "./search/RDMRecordMultipleSearchBarElement";
import { RelatedWorksField } from "./fields/RelatedWorksField";
import { ResultOptions } from "./search/ResultOptions";
import { SearchAppLayout } from "./search/SearchAppLayout";
import { SubjectsField } from "./fields/SubjectsField";
import { TitlesField } from "./fields/TitlesField";
import { VersionField } from "./fields/VersionField";
import { FileUploader } from "./fields/file_uploader_components/index";


const MobileActionMenu = () => {
  return (
    <div className="col-12">
      <h1>HERE IT IS</h1>
    </div>
  );
};

const SearchAppLayoutWithConfig = parametrize(SearchAppLayout, {
  appName: "InvenioAppRdm.Search",
});

const DashboardRequestsSearchLayoutWithApp = parametrize(RequestsSearchLayout, {
  appName: "InvenioAppRdm.DashboardRequests",
});

const CommunityRequestsSearchLayoutWithApp = parametrize(RequestsSearchLayout, {
  appName: "InvenioCommunities.RequestSearch",
});

export const overriddenComponents = {
  "InvenioAppRdm.DashboardRequests.SearchApp.layout": DashboardRequestsSearchLayoutWithApp,
  "InvenioAppRdm.DashboardRequests.ResultsList.item": RequestsResultsItemTemplateDashboard,
  "InvenioAppRdm.Deposit.AccessRightField.container": AccessRightField,
  "InvenioAppRdm.Deposit.CreatorsField.container": CreatibutorsField,
  "InvenioAppRdm.Deposit.ContributorsField.container": CreatibutorsField,
  "InvenioAppRdm.Deposit.DescriptionsField.container": DescriptionsField,
  "InvenioAppRdm.Deposit.FormFeedback.container": FormFeedback,
  "InvenioAppRdm.Deposit.FileUploader.container": FileUploader,
  "InvenioAppRdm.Deposit.FundingField.container": FundingField,
  "InvenioAppRdm.Deposit.IdentifiersField.container": IdentifiersField,
  "InvenioAppRdm.Deposit.LicenseField.container": LicenseField,
  "InvenioAppRdm.Deposit.PublicationDateField.container": PublicationDateField,
  "InvenioAppRdm.Deposit.PublisherField.container": PublisherField,
  "InvenioAppRdm.Deposit.RelatedWorksField.container": RelatedWorksField,
  "InvenioAppRdm.Deposit.SubjectsField.container": SubjectsField,
  "InvenioAppRdm.Deposit.TitlesField.container": TitlesField,
  "InvenioAppRdm.Deposit.VersionField.container": VersionField,
  "InvenioAppRdm.RecordsList.RecordsResultsListItem.layout": RecordsResultsListItem,
  "InvenioAppRDM.RecordsList.RecordsResultsListItem.layout": RecordsResultsListItem,
  "InvenioAppRdm.Search.RecordsResultsListItem.layout": RecordsResultsListItem,
  "InvenioAppRdm.Search.SearchBar.element": RDMRecordMultipleSearchBarElement,
  "InvenioAppRdm.Search.SearchApp.layout": SearchAppLayoutWithConfig,
  "InvenioAppRdm.Search.SearchApp.resultOptions": ResultOptions,
  "InvenioCommunities.CommunityPrivilegesForm.layout": CommunityPrivilegesFormLayout,
  "InvenioCommunities.CurationPolicyForm.layout": CurationPolicyFormLayout,
  "InvenioCommunities.CommunityProfileForm.GridRow.DangerZone": DangerZone,
  "InvenioCommunities.CommunityProfileForm.LogoUploader.ProfilePicture": LogoUploader,
  "InvenioCommunities.DetailsSearch.ResultsList.item": RecordsResultsListItem,
  "InvenioCommunities.RequestSearch.ResultsList.item": RequestsResultsItemTemplateWithCommunity,
  "InvenioCommunities.RequestSearch.SearchApp.layout": CommunityRequestsSearchLayoutWithApp,
  "InvenioCommunities.InvitationsSearch.ResultsList.item": InvitationResultItemWithConfig,
  "InvenioCommunities.ManagerSearch.ResultsList.item": ManagerMembersResultItemWithConfig,
  "InvenioCommunities.ManagerSearch.SearchBar.element": MembersSearchBarElement,
  "InvenioCommunities.MemberSearch.ResultsList.item": ManagerMembersResultItemWithConfig,
  "InvenioCommunities.MemberSearch.SearchBar.element": MembersSearchBarElement,
  "InvenioCommunities.PublicSearch.ResultsList.item": PublicMembersResultsItemWithCommunity,
  "InvenioCommunities.PublicSearch.SearchBar.element": MembersSearchBarElement,
  "InvenioModularDetailPage.MobileActionMenu.container": MobileActionMenu,
  // "InvenioAppRdm.Deposit.ResourceTypeField.container": ResourceTypeField
  // InvenioCommunities.Search.SearchApp.layout: CommunityRecordsSearchAppLayout,
  "InvenioRequest.RequestMetadata.Layout": RequestMetadata,
  "ReactInvenioDeposit.MetadataOnlyToggle.layout": MetadataOnlyToggle,
};
