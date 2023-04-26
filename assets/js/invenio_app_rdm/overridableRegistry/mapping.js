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

  import React from "react";
  import { Checkbox } from "semantic-ui-react";
  import { useFormikContext } from "formik";
  import PropTypes from "prop-types";

  const MetadataOnlyToggle = (props) => {
    const { filesEnabled } = props;
    const { setFieldValue } = useFormikContext();

    const handleOnChangeMetadataOnly = () => {
      setFieldValue("files.enabled", !filesEnabled);
      setFieldValue("access.files", "public");
    };

    return (
      <Checkbox
        toggle
        label="Metadata-only record"
        onChange={handleOnChangeMetadataOnly}
      />
    );
  };

  MetadataOnlyToggle.propTypes = {
    filesEnabled: PropTypes.bool.isRequired,
  };

export default MetadataOnlyToggle;

export const overriddenComponents = {
    "ReactInvenioDeposit.MetadataOnlyToggle.layout": MetadataOnlyToggle
}