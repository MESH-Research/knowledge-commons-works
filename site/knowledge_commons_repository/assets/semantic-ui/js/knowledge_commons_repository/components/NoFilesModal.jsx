import { i18next } from "@translations/invenio_rdm_records/i18next";
import React, { useState, useContext } from "react";
import { connect } from "react-redux";
import { useFormikContext } from "formik";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "@js/invenio_rdm_records";
import { Button, Header, Icon, Modal } from "semantic-ui-react";
import _omit from "lodash/omit";
import PropTypes from "prop-types";

const DRAFT_PREVIEW_STARTED = "DRAFT_PREVIEW_STARTED";
const DRAFT_SAVE_STARTED = "DRAFT_SAVE_STARTED";

const NoFilesModalComponent = ({actionName,
                       actionState=undefined,
                       handleConfirmNoFiles,
                       handleConfirmNeedsFiles,
                       sanitizeDataForSaving,
                       missingFiles,
                       ...ui
                      }) => {

  const { handleSubmit, isSubmitting } = useFormikContext();
  const { setSubmitContext } = useContext(DepositFormSubmitContext);
  const [ open, setOpen ] = useState(false);
  const uiProps = _omit(ui, ["dispatch"]);

  const handleOpen = () => setOpen(true);

  const handleCancel = () => {
    if ( missingFiles ) {
        handleConfirmNeedsFiles();
    }
    setOpen(false);
  };

  const actions = {
    preview: {
      name: "preview",
      buttonLabel: i18next.t("Preview"),
      icon: "eye",
      action: DepositFormSubmitActions.PREVIEW,
      newActionState: DRAFT_PREVIEW_STARTED,
    },
    saveDraft: {
      name: "save",
      buttonLabel: i18next.t("Save draft"),
      icon: "save",
      action: DepositFormSubmitActions.SAVE,
      newActionState: DRAFT_SAVE_STARTED,
    }
  }
  const { name, buttonLabel, icon, action, newActionState } = actions[actionName];

  const handlePositive = (event) => {
    console.log(actions[actionName]);
    sanitizeDataForSaving().then(handleConfirmNoFiles()).then(() => {
        setSubmitContext(action);
        handleSubmit(event);
        setOpen(false);
    });
  };

  return (
    <>
    <Button
      name={name}
      disabled={isSubmitting}
      onClick={missingFiles ? handleOpen : handlePositive}
      loading={isSubmitting && actionState === newActionState}
      icon={icon}
      labelPosition="left"
      content={buttonLabel}
      type={missingFiles ? "button" : "submit"}
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
        <Button color='green' onClick={handlePositive}>
          <Icon name='checkmark' /> Yes, continue without files
        </Button>
      </Modal.Actions>
    </Modal>
    </>
)
}

NoFilesModalComponent.propTypes = {
  actionState: PropTypes.string,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  record: state.deposit.record,
});

export const NoFilesModal = connect(
  mapStateToProps,
  null
)(NoFilesModalComponent);