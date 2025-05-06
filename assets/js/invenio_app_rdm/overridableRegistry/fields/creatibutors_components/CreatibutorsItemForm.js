import React, { useState } from "react";
import PropTypes from "prop-types";
import { Form, Header, Transition } from "semantic-ui-react";
import { getIn } from "formik";
import _get from "lodash/get";
import _find from "lodash/find";
import _isEmpty from "lodash/isEmpty";
import _map from "lodash/map";
import { i18next } from "@translations/i18next";
import { Trans } from "react-i18next";
import { CreatibutorsFormBody } from "./CreatibutorsFormBody";
import { CreatibutorsFormActionButtons } from "./CreatibutorsFormActionButtons";

const NamesAutocompleteOptions = {
  SEARCH: "search",
  SEARCH_ONLY: "search_only",
  OFF: "off",
};

/**
 * Subform for adding or editing creatibutors.
 *
 */
const CreatibutorsItemForm = ({
  addCreatibutor,
  addLabel,
  autocompleteNames = "search",
  fieldPath,
  fieldPathPrefix,
  focusAddButtonHandler,
  handleCancel,
  handleCloseForm,
  index,
  isCreator,
  isNewItem,
  removeCreatibutor,
  roleOptions = [],
  values,
}) => {
  const [saveAndContinueLabel, setSaveAndContinueLabel] = useState(
    i18next.t("Save and add another")
  );
  const [show, setShow] = useState(true);
  const [showPersonForm, setShowPersonForm] = useState(
    autocompleteNames !== NamesAutocompleteOptions.SEARCH_ONLY ||
      !_isEmpty(getIn(values, fieldPathPrefix))
  );
  const showManualEntry =
    autocompleteNames === NamesAutocompleteOptions.SEARCH_ONLY &&
    !showPersonForm;

  const changeContent = () => {
    setSaveAndContinueLabel(i18next.t("Added"));
    // change in 2 sec
    setTimeout(() => {
      setSaveAndContinueLabel(i18next.t("Save and add another"));
    }, 2000);
  };

  const handleSave = (action) => {
    setShow(false);
    window.setTimeout(() => {
      handleCloseForm(addCreatibutor, index, action);
      if (action == "saveAndContinue") {
        changeContent();
      }
    }, 100);
  };

  return (
    <Transition
      visible={show}
      animation="fade"
      duration={300}
      transitionOnMount={true}
    >
      <div className={`${fieldPath}-item-form ui form`}>
        {isNewItem ? <Header as="h2">{addLabel}</Header> : null}
        <CreatibutorsFormBody
          {...{
            autocompleteNames,
            fieldPath,
            fieldPathPrefix,
            index,
            isCreator,
            isNewItem,
            roleOptions,
            showManualEntry,
            showPersonForm,
            values,
          }}
        />
        <Form.Group inline className="creatibutors-item-form-buttons">
          <CreatibutorsFormActionButtons
            {...{
              autocompleteNames,
              handleCancel,
              handleSave,
              index,
              isNewItem,
              removeCreatibutor,
              saveAndContinueLabel,
              setShowPersonForm,
            }}
          />
        </Form.Group>
      </div>
    </Transition>
  );
};

CreatibutorsItemForm.propTypes = {
  addLabel: PropTypes.string.isRequired,
  autocompleteNames: PropTypes.string,
  fieldPath: PropTypes.string.isRequired,
  fieldPathPrefix: PropTypes.string.isRequired,
  focusAddButtonHandler: PropTypes.func,
  handleCancel: PropTypes.func.isRequired,
  handleCloseForm: PropTypes.func.isRequired,
  index: PropTypes.number.isRequired,
  isCreator: PropTypes.bool,
  isNewItem: PropTypes.bool,
  roleOptions: PropTypes.array,
  values: PropTypes.object.isRequired,
};

export { CreatibutorsItemForm, NamesAutocompleteOptions };
