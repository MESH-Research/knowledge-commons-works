// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import React, { useState, useContext } from "react";
import { connect } from "react-redux";
import { Button, Header, Icon, Modal } from "semantic-ui-react";
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

const SaveButtonComponent = ({ actionState=undefined,
                               handleConfirmNoFiles,
                               handleConfirmNeedsFiles,
                               sanitizeDataForSaving,
                               missingFiles,
                               hasFiles,
                               filesEnabled,
                               ...ui }) => {

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

  const handleSave = (event) => {
    sanitizeDataForSaving().then(handleConfirmNoFiles()).then(() => {
        setSubmitContext(DepositFormSubmitActions.SAVE);
        handleSubmit(event);
        scrollTop();
        setOpen(false);
    });
  }

  return (
    <>
    <Button
      name="save"
      disabled={isSubmitting}
      onClick={missingFiles ? handleOpen : handleSave }
      icon="save"
      loading={isSubmitting && actionState === DRAFT_SAVE_STARTED}
      labelPosition="left"
      content={i18next.t("Save draft")}
      {...uiProps}
    />
    <Modal
      closeIcon
      open={open}
    //   trigger={<Button>Show Modal</Button>}
      onClose={() => setOpen(false)}
      onOpen={() => setOpen(true)}
    >
      <Header icon='archive' content='No files included' />
      <Modal.Content>
        <p>
          Are you sure you want to save this draft without any uploaded files?
        </p>
      </Modal.Content>
      <Modal.Actions>
        <Button color='red' onClick={handleCancel}>
          <Icon name='remove' /> No, let me add files
        </Button>
        <Button color='green' onClick={handleSave}>
          <Icon name='checkmark' /> Yes, continue without files
        </Button>
      </Modal.Actions>
    </Modal>
    </>
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
