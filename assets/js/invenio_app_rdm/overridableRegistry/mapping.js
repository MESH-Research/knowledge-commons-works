// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

/**
 * Add here all the overridden components of your app.
 */
// import React from "react";
//   import { Checkbox, List, Popup, Icon } from "semantic-ui-react";

// const MetadataOnlyToggle =  (props) => {
//   return(
//   <div
//     id="ReactInvenioDeposit.FileUploaderToolbar.MetadataOnlyToggle.container"
//     filesList={props.filesList}
//     filesEnabled={props.filesEnabled}
//     handleOnChangeMetadataOnly={props.handleOnChangeMetadataOnly}
//     >
//     {props.showMetadataOnlyToggle && (
//         <List horizontal>
//         <List.Item>
//             <Checkbox
//             toggle
//             label={props.i18next.t("Metadata-only record switch")}
//             onChange={props.handleOnChangeMetadataOnly}
//             disabled={props.filesList.length > 0}
//             checked={!props.filesEnabled}
//             />
//         </List.Item>
//         <List.Item>
//             <Popup
//             trigger={
//                 <Icon name="question circle outline" className="neutral" />
//             }
//             content={props.i18next.t("Disable files for this record")}
//             position="top center"
//             />
//         </List.Item>
//         </List>
//     )}
//   </div>
//   );
// }
import { CreatibutorsField } from "./fields/CreatibutorsField";
import { FundingField } from "./fields/FundingField";
import { IdentifiersField } from "./fields/IdentifiersField";
import { MetadataOnlyToggle } from "./fields/MetadataOnlyToggle";
import { PublisherField } from "./fields/PublisherField";
import { RelatedWorksField } from "./fields/RelatedWorksField";
import { TitlesField } from "./fields/TitlesField";
import { VersionField } from "./fields/VersionField";

export const overriddenComponents = {
    "ReactInvenioDeposit.MetadataOnlyToggle.layout": MetadataOnlyToggle,
    "InvenioAppRdm.Deposit.CreatorsField.container": CreatibutorsField,
    "InvenioAppRdm.Deposit.ContributorsField.container": CreatibutorsField,
    "InvenioAppRdm.Deposit.FundingField.container": FundingField,
    "InvenioAppRdm.Deposit.PublisherField.container": PublisherField,
    "InvenioAppRdm.Deposit.IdentifiersField.container": IdentifiersField,
    "InvenioAppRdm.Deposit.VersionField.container": VersionField,
    "InvenioAppRdm.Deposit.RelatedWorksField.container": RelatedWorksField,
    "InvenioAppRdm.Deposit.TitlesField.container": TitlesField,
    // "InvenioAppRdm.Deposit.ResourceTypeField.container": ResourceTypeField
}