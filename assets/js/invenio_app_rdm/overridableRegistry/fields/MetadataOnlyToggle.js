// This file is part of the Knowledge Commons Repository
// a customized deployment of InvenioRDM
// Copyright (C) 2023 MESH Research.
// InvenioRDM Copyright (C) 2023 CERN.
//
// Invenio App RDM and the Knowledge Commons Repository are free software;
// you can redistribute them and/or modify them
// under the terms of the MIT License; see LICENSE file for more details.

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

export { MetadataOnlyToggle };