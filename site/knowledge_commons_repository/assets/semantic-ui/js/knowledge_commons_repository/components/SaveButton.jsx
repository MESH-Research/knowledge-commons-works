// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import React, { useState, useContext } from "react";
import { connect } from "react-redux";
import { Button } from "semantic-ui-react";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "@js/invenio_rdm_records";
// import { DRAFT_SAVE_STARTED } from "../../state/types";
import { scrollTop } from "../utils";
// import { scrollTop } from "../../utils";
import _omit from "lodash/omit";
import { useFormikContext } from "formik";
import PropTypes from "prop-types";

export const DRAFT_SAVE_STARTED = "DRAFT_SAVE_STARTED";

const SaveButtonComponent = ({ actionState=undefined, ...ui }) => {

  const { handleSubmit, isSubmitting } = useFormikContext();
  const { setSubmitContext } = useContext(DepositFormSubmitContext);
  const uiProps = _omit(ui, ["dispatch"]);
  const [ open, setOpen ] = useState(false);

  const show = () => this.setState({ open: true })
  const handleConfirm = () => { setConfirmedNoFiles(true); setOpen(false) };
  const handleCancel = () => { setConfirmedNoFiles(false); setOpen(false) };

  const handleSave = (event) => {
    setSubmitContext(DepositFormSubmitActions.SAVE);
    handleSubmit(event);
    scrollTop()
  };

  return (
    <Button
      name="save"
      disabled={isSubmitting}
      onClick={handleSave}
      icon="save"
      loading={isSubmitting && actionState === DRAFT_SAVE_STARTED}
      labelPosition="left"
      content={i18next.t("Save draft")}
      {...uiProps}
    />
  );
}

SaveButtonComponent.propTypes = {
  actionState: PropTypes.string,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
});

export const SaveButton = connect(
  mapStateToProps,
  null
)(SaveButtonComponent);
