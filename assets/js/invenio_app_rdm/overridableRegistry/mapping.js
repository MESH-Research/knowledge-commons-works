// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { CreatibutorsField } from "./fields/CreatibutorsField";
import { DescriptionsField } from "./fields/DescriptionsField";
import { FundingField } from "./fields/FundingField";
import { IdentifiersField } from "./fields/IdentifiersField";
import { MetadataOnlyToggle } from "./fields/MetadataOnlyToggle";
import { PublicationDateField } from "./fields/PublicationDateField";
import { PublisherField } from "./fields/PublisherField";
import { RelatedWorksField } from "./fields/RelatedWorksField";
import { SubjectsField } from "./fields/SubjectsField";
import { TitlesField } from "./fields/TitlesField";
import { VersionField } from "./fields/VersionField";

export const overriddenComponents = {
    "InvenioAppRdm.Deposit.CreatorsField.container": CreatibutorsField,
    "InvenioAppRdm.Deposit.ContributorsField.container": CreatibutorsField,
    "InvenioAppRdm.Deposit.DescriptionsField.container": DescriptionsField,
    "InvenioAppRdm.Deposit.FundingField.container": FundingField,
    "InvenioAppRdm.Deposit.IdentifiersField.container": IdentifiersField,
    "ReactInvenioDeposit.MetadataOnlyToggle.layout": MetadataOnlyToggle,
    "InvenioAppRdm.Deposit.PublicationDateField.container": PublicationDateField,
    "InvenioAppRdm.Deposit.PublisherField.container": PublisherField,
    "InvenioAppRdm.Deposit.RelatedWorksField.container": RelatedWorksField,
    "InvenioAppRdm.Deposit.TitlesField.container": TitlesField,
    "InvenioAppRdm.Deposit.VersionField.container": VersionField,
    "InvenioAppRdm.Deposit.SubjectsField.container": SubjectsField,
    // "InvenioAppRdm.Deposit.ResourceTypeField.container": ResourceTypeField
}