// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2022 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import React, { Component } from "react";
import { connect } from "react-redux";
import { connect as connectFormik } from "formik";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "@js/invenio_rdm_records";
// import { DRAFT_PREVIEW_STARTED } from "../../state/types";
import { Button } from "semantic-ui-react";
import _omit from "lodash/omit";
import PropTypes from "prop-types";

const DRAFT_PREVIEW_STARTED = "DRAFT_PREVIEW_STARTED";

const PreviewButtonComponent = ({actionState=undefined,
                                 handleConfirmNoFiles,
                                 handleConfirmNeedsFiles,
                                 sanitizeDataForSaving,
                                 missingFiles,
                                 hasFiles,
                                 filesEnabled,
                                 ...ui}) => {

  const { handleSubmit, isSubmitting } = useFormikContext();
  const { setSubmitContext } = useContext(DepositFormSubmitContext);
  const uiProps = _omit(ui, ["dispatch"]);
  const [ open, setOpen ] = useState(false);

  const handleOpen = () => setOpen(true);

  const handleCancel = () => {
    if ( missingFiles ) {
        handleConfirmNeedsFiles();
    }
    setOpen(false);
  };

  const handlePreview = (event) => {
    sanitizeDataForSaving().then(handleConfirmNoFiles()).then(() => {
        setSubmitContext(DepositFormSubmitActions.PREVIEW);
        handleSubmit(event);
        setOpen(false);
    });
  };

  return (
    <>
    <Button
      name="preview"
      disabled={isSubmitting}
      onClick={missingFiles ? handleOpen : handlePreview}
      loading={isSubmitting && actionState === DRAFT_PREVIEW_STARTED}
      icon="eye"
      labelPosition="left"
      content={i18next.t("Preview")}
      {...uiProps}
    />
    <NoFilesModal handleCancel={handleCancel}
        handlePositive={handlePreview}
        open={open}
    />
    </>
  );
}

PreviewButtonComponent.propTypes = {
  actionState: PropTypes.string,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  record: state.deposit.record,
});

export const PreviewButton = connect(
  mapStateToProps,
  null
)(PreviewButtonComponent);
