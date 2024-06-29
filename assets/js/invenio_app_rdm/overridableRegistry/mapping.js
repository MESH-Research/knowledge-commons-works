// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { parametrize } from "react-overridable";

import { AccessRightField } from "./fields/AccessRightField";
import { CreatibutorsField } from "./fields/CreatibutorsField";
import { DescriptionsField } from "./fields/DescriptionsField";
import { FormFeedback } from "./fields/FormFeedback";
import { FundingField } from "./fields/FundingField";
import { IdentifiersField } from "./fields/IdentifiersField";
import { LicenseField } from "./fields/LicenseField";
import { MetadataOnlyToggle } from "./fields/MetadataOnlyToggle";
import { PublicationDateField } from "./fields/PublicationDateField";
import { PublisherField } from "./fields/PublisherField";
import RecordsResultsListItem from "./search/RecordsResultsListItem";
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

export const overriddenComponents = {
  "InvenioAppRdm.Deposit.AccessRightField.container": AccessRightField,
  "InvenioAppRdm.Deposit.CreatorsField.container": CreatibutorsField,
  "InvenioAppRdm.Deposit.ContributorsField.container": CreatibutorsField,
  "InvenioAppRdm.Deposit.DescriptionsField.container": DescriptionsField,
  "InvenioAppRdm.Deposit.FormFeedback.container": FormFeedback,
  "InvenioAppRdm.Deposit.FundingField.container": FundingField,
  "InvenioAppRdm.Deposit.IdentifiersField.container": IdentifiersField,
  "InvenioAppRdm.Deposit.LicenseField.container": LicenseField,
  "ReactInvenioDeposit.MetadataOnlyToggle.layout": MetadataOnlyToggle,
  "InvenioAppRdm.Deposit.PublicationDateField.container": PublicationDateField,
  "InvenioAppRdm.Deposit.PublisherField.container": PublisherField,
  "InvenioAppRdm.RecordsList.RecordsResultsListItem.layout": RecordsResultsListItem,
  "InvenioAppRDM.RecordsList.RecordsResultsListItem.layout": RecordsResultsListItem,
  "InvenioAppRdm.Search.RecordsResultsListItem.layout": RecordsResultsListItem,
  "InvenioAppRdm.Search.SearchBar.element": RDMRecordMultipleSearchBarElement,
  "InvenioAppRdm.Search.SearchApp.layout": SearchAppLayoutWithConfig,
  "InvenioAppRdm.Search.SearchApp.resultOptions": ResultOptions,
  "InvenioAppRdm.Deposit.RelatedWorksField.container": RelatedWorksField,
  "InvenioAppRdm.Deposit.TitlesField.container": TitlesField,
  "InvenioAppRdm.Deposit.VersionField.container": VersionField,
  "InvenioAppRdm.Deposit.SubjectsField.container": SubjectsField,
  "InvenioAppRdm.Deposit.FileUploader.container": FileUploader,
  "InvenioCommunities.DetailsSearch.ResultsList.item": RecordsResultsListItem,
  "InvenioModularDetailPage.MobileActionMenu.container": MobileActionMenu,
  // "InvenioAppRdm.Deposit.ResourceTypeField.container": ResourceTypeField
  // InvenioCommunities.Search.SearchApp.layout: CommunityRecordsSearchAppLayout,
};
