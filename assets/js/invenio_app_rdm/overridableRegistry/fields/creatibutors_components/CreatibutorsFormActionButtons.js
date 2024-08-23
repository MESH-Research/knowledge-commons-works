import React from "react";
import PropTypes from "prop-types";
import { Button, ButtonGroup } from "semantic-ui-react";
import _get from "lodash/get";
import _find from "lodash/find";
import _isEmpty from "lodash/isEmpty";
import _map from "lodash/map";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Trans } from "react-i18next";
import { ModalActions, NamesAutocompleteOptions } from "./CreatibutorsItemForm";

const CreatibutorsFormActionButtons = ({
  autocompleteNames,
  handleCancel,
  handleSave,
  index,
  isNewItem,
  removeCreatibutor,
  saveAndContinueLabel,
  setShowPersonForm,
}) => {
  console.log( "CreatibutorsFormActionButtons index", index );

  return (
    <>
      <Button
        name="cancel"
        onClick={() => {
          handleCancel(removeCreatibutor, index);
        }}
        icon="remove"
        content={i18next.t("Cancel")}
        floated="left"
      />
      <div className="right-buttons right floated">
      {isNewItem && (
        <Button
          name="saveAndContinue"
          onClick={() => {
            setShowPersonForm(
              autocompleteNames !== NamesAutocompleteOptions.SEARCH_ONLY
            );
            handleSave("saveAndContinue");
          }}
          primary
          icon="checkmark"
          content={saveAndContinueLabel}
        />
      )}
      <Button
        name="save"
        onClick={() => {
          setShowPersonForm(
            autocompleteNames !== NamesAutocompleteOptions.SEARCH_ONLY
          );
          handleSave("saveAndClose");
        }}
        primary
        icon="checkmark"
        content={i18next.t("Save")}
      />
      </div>
    </>
  );
};

CreatibutorsFormActionButtons.propTypes = {
    autocompleteNames: PropTypes.string.isRequired,
    handleCancel: PropTypes.func.isRequired,
    handleSave: PropTypes.func.isRequired,
    index: PropTypes.number.isRequired,
    removeCreatibutor: PropTypes.func.isRequired,
    saveAndContinueLabel: PropTypes.string.isRequired,
    setShowPersonForm: PropTypes.func.isRequired,
    };

export { CreatibutorsFormActionButtons };