// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/i18next";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import _isObject from "lodash/isObject";
import _merge from "lodash/merge";
import React, { useEffect } from "react";
import { connect } from "react-redux";
import { Message } from "semantic-ui-react";
import {
  DISCARD_PID_FAILED,
  DRAFT_DELETE_FAILED,
  DRAFT_HAS_VALIDATION_ERRORS,
  DRAFT_PREVIEW_FAILED,
  DRAFT_PUBLISH_FAILED,
  DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS,
  DRAFT_SAVE_FAILED,
  DRAFT_SAVE_SUCCEEDED,
  DRAFT_SUBMIT_REVIEW_FAILED,
  DRAFT_SUBMIT_REVIEW_FAILED_WITH_VALIDATION_ERRORS,
  FILE_IMPORT_FAILED,
  FILE_UPLOAD_SAVE_DRAFT_FAILED,
  RESERVE_PID_FAILED,
} from "./types";
import { leafTraverse } from "@js/invenio_rdm_records"; // ../utils
import PropTypes from "prop-types";
import { flattenKeysDotJoined } from "@js/invenio_modular_deposit_form/utils";
import { useFormikContext } from "formik";

const readableMessageEquivalents = {
  "Missing data for required field.": "Missing a value for a required field.",
  "Field may not be null.": "Field cannot be empty.",
};

const defaultFieldLabels = {
  "custom_fields.kcr:ai_usage": i18next.t("AI usage"),
  "custom_fields.kcr:ai_usage.ai_used": i18next.t("AI usage"),
  "files.enabled": i18next.t("Files"),
  "metadata.resource_type": i18next.t("Resource type"),
  "metadata.title": i18next.t("Title"),
  "metadata.additional_titles": i18next.t("Additional titles"),
  "metadata.publication_date": i18next.t("Publication date"),
  "metadata.creators": i18next.t("Creators/Contributors"),
  "metadata.contributors": i18next.t("Creators/Contributors"),
  "metadata.description": i18next.t("Abstract/Description"),
  "metadata.additional_descriptions": i18next.t("Additional descriptions"),
  "metadata.rights": i18next.t("Licenses"),
  "metadata.languages": i18next.t("Languages"),
  "metadata.dates": i18next.t("Dates"),
  "metadata.version": i18next.t("Version"),
  "metadata.publisher": i18next.t("Publisher"),
  "metadata.related_identifiers": i18next.t("Related works"),
  "metadata.references": i18next.t("References"),
  "metadata.identifiers": i18next.t("Alternate identifiers"),
  "metadata.subjects": i18next.t("Keywords and subjects"),
  "access.embargo.until": i18next.t("Embargo until"),
  "pids.doi": i18next.t("DOI"),
  pids: i18next.t("DOI"),
};

const ACTIONS = {
  ["ERRORS_CLEARED"]: {
    feedback: "positive",
    message: undefined,
  },
  ["CLIENT_VALIDATION_ERRORS"]: {
    feedback: "negative",
    message: i18next.t("Please correct the errors in the form"),
  },
  [DRAFT_SAVE_SUCCEEDED]: {
    feedback: "positive",
    message: i18next.t("Draft successfully saved"),
  },
  [DRAFT_HAS_VALIDATION_ERRORS]: {
    feedback: "warning",
    message: i18next.t("Draft saved, but some field values could not be accepted"),
  },
  [DRAFT_SAVE_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Draft was not saved. Please try again. If the problem persists, contact user support."
    ),
  },
  [DRAFT_PUBLISH_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Draft was not published. Please try again. If the problem persists, contact user support."
    ),
  },
  [DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS]: {
    feedback: "negative",
    message: i18next.t(
      "Draft was saved but not published. Some field values could not be accepted:"
    ),
  },
  [DRAFT_SUBMIT_REVIEW_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Draft was not submitted for review. Please try again. If the problem persists, contact user support."
    ),
  },
  [DRAFT_SUBMIT_REVIEW_FAILED_WITH_VALIDATION_ERRORS]: {
    feedback: "negative",
    message: i18next.t(
      "Draft was saved but not submitted for review. Some field values could not be accepted:"
    ),
  },
  [DRAFT_DELETE_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Draft was not deleted. Please try again. If the problem persists, contact user support."
    ),
  },
  [DRAFT_PREVIEW_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Draft preview failed. Please try again. If the problem persists, contact user support."
    ),
  },
  [RESERVE_PID_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "DOI reservation failed. Please try again. If the problem persists, contact user support."
    ),
  },
  [DISCARD_PID_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "DOI could not be discarded. Please try again. If the problem persists, contact user support."
    ),
  },
  [FILE_UPLOAD_SAVE_DRAFT_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Draft save failed before file upload. Please try again. If the problem persists, contact user support."
    ),
  },
  [FILE_IMPORT_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Files were not imported from the previous version. Please try again. If the problem persists, contact user support."
    ),
  },
};

/**
 * Class to handle error message processing and formatting
 */
class ErrorMessageHandler {
  /**
   * Replace select error messages with more readable equivalents
   * @param {string} error
   * @returns {string}
   */
  static makeErrorReadable(error) {
    if (readableMessageEquivalents[error]) {
      return readableMessageEquivalents[error];
    }
    return error;
  }

  /**
   * Convert each value in object to array of messages.
   *
   * Returns an object with field paths as keys and lists of messages
   * for those fields as the values.
   *
   * @param {object} errorObj
   * @returns {object}
   */
  static errorsToMessageArrays(errorObj) {
    const messagesToArray = (errorValue) => {
      let messages = [];
      let store = (l) => {
        messages.push(l);
      };
      leafTraverse(errorValue, store);
      return messages;
    };

    const errors = Object.fromEntries(
      Object.entries(errorObj).map(([key, value]) => {
        return [key, messagesToArray(value)];
      })
    );

    return errors;
  }

  /**
   * Convert error object with nested object structure to object with field names as keys.
   *
   * Create object with collapsed 1st and 2nd level keys
   *   e.g., {metadata: {creators: ,,,}} => {"metadata.creators": ...}
   * For now, only for metadata, files and access.embargo
   *
   * @param {object} errors
   * @returns {object}
   */
  static collapseKeysIntoFieldLabels(errors) {
    const metadata = Object.entries(errors?.metadata || {}).map(([key, value]) => {
      return ["metadata." + key, value];
    });
    const files = Object.entries(errors?.files || {}).map(([key, value]) => {
      return ["files." + key, value];
    });
    const access = Object.entries(errors?.access || {}).map(([key, value]) => {
      return ["access.embargo." + key, value];
    });
    const customFields = Object.entries(errors?.custom_fields || {}).map(
      ([key, value]) => {
        console.log("FormFeedback rendering custom_fields:", key, value);
        return ["custom_fields." + `${key}`, value];
      }
    );
    let combinedFieldLabels = metadata.concat(files).concat(access).concat(customFields);
    console.log("FormFeedback rendering combined collapsed keys:", combinedFieldLabels);
    console.log("FormFeedback rendering errors.pids:", errors?.pids);
    if (errors?.pids) {
      const pids = _isObject(errors?.pids)
        ? Object.entries(errors?.pids || {}).map(([key, value]) => {
            return ["pids." + key, value];
          })
        : [["pids", errors?.pids || {}]];
      combinedFieldLabels = combinedFieldLabels.concat(pids);
    }
    const collapsedErrors = Object.fromEntries(combinedFieldLabels);
    return collapsedErrors;
  }

  /**
   * Group error messages by label
   *
   * Different field paths (error object keys) can map to same label, e.g. title and
   * additional_titles for metadata.titles. This collapses these to use the same title.
   *
   * @param {object} errors
   * @param {object} labels
   * @returns {object}
   */
  static groupMessagesByLabel(errors, labels) {
    const groupedErrorMessages = {};
    for (const key in errors) {
      const label = labels[key] || key;
      let messages = groupedErrorMessages[label] || [];
      groupedErrorMessages[label] = messages.concat(errors[key]);
    }
    return groupedErrorMessages;
  }

  /**
   * Return object with human readable labels as keys and error messages as
   * values given an errors object.
   *
   * For now this handles only errors in metadata, files, access.embargo,
   * custom_fields and pids.
   *
   * @param {object} errors
   * @param {object} labels
   * @returns {object}
   */
  static toLabelledErrorMessages(errors, labels) {
    // Step 1 - Create object with collapsed 1st and 2nd level keys
    const collapsedPathsWithErrors = this.collapseKeysIntoFieldLabels(errors);

    // Step 2 - Convert error objects to arrays of messages
    const pathsWithMessageArrays = this.errorsToMessageArrays(collapsedPathsWithErrors);

    // Step 3 - Make error messages more readable
    const pathsWithReadableArrays = Object.fromEntries(
      Object.entries(pathsWithMessageArrays).map(([key, value]) => {
        return [key, value.map((v) => this.makeErrorReadable(v))];
      })
    );

    // Step 4 - Group messages by their labels
    const labelsWithGroupedMessages = this.groupMessagesByLabel(
      pathsWithReadableArrays,
      labels
    );

    return labelsWithGroupedMessages;
  }
}

/**
 * FormFeedback component
 *
 * This component displays error messages for the deposit form.
 *
 * Note: the `errors` prop carries the backend error state as it stood after
 * the last form submission, coming from the Redux store. The `clientErrors`
 * prop carries the client errors as they are currently in the formik context,
 * coming from the formik `errors` object. Since the Redux store is not
 * currently updated as form values change, it will be out of date most of the
 * time. Backend validation errors are added to the formik state and managed there.
 * For the accurate current state of any field validation errors we need to use
 * the `clientErrors` prop.
 *
 * The Redux store `errors` prop will, though, carry other errors that are not
 * related to validation, such as file upload errors.
 *
 * The `nonValidationErrors` prop carries these other errors from the Redux store,
 * already filtered out of the Redux `errors` object.
 *
 * @param {object} props
 * @param {object} props.errors - The errors object from the deposit form.
 * @param {string} props.actionState - The action state of the deposit form.
 * @param {object} props.clientErrors - The client errors object from the deposit form.
 * @param {object} props.nonValidationErrors - The non-validation errors object from the deposit form.
 * @param {object} props.labels - The labels object from the deposit form.
 */
const DisconnectedFormFeedback = ({
  errors,
  actionState,
  clientErrors,
  nonValidationErrors,
  labels,
  ...rest
}) => {
  const mergedLabels = {
    ...defaultFieldLabels,
    ...labels,
  };

  const { setFieldTouched } = useFormikContext();

  // Set the touched state for all error fields
  // This is to ensure that the error fields are flagged when the form is submitted
  useEffect(() => {
    const flattenedErrors = clientErrors ? flattenKeysDotJoined(clientErrors) : [];
    flattenedErrors.forEach((errorField) => {
      setFieldTouched(errorField, true);
    });
  }, [clientErrors]);

  /**
   * Render error messages inline (if 1) or as list (if multiple).
   *
   * @param {Array<String>} messages
   * @returns String or React node
   */
  const renderErrorMessages = (messages) => {
    const uniqueMessages = [...new Set(messages)];
    if (uniqueMessages.length === 1) {
      return messages[0];
    } else {
      return (
        <ul>
          {uniqueMessages.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      );
    }
  };

  // console.log("FormFeedback rendering errors:", errors);
  // console.log("FormFeedback rendering clientErrors:", clientErrors);
  // console.log("FormFeedback rendering nonValidationErrors:", nonValidationErrors);
  // console.log("FormFeedback rendering rest:", rest);

  const combinedActionState = !_isEmpty(clientErrors)
    ? "CLIENT_VALIDATION_ERRORS"
    : (
      _isEmpty(nonValidationErrors) &&
      _isEmpty(clientErrors) &&
      actionState?.includes("ERROR")
    )
    ? "ERRORS_CLEARED"
    : actionState;

  const { feedback, message } = _get(ACTIONS, combinedActionState, {
    feedback: undefined,
    message: undefined,
  });
  // console.log("FormFeedback rendering feedback:", feedback);
  // console.log("FormFeedback rendering message:", message);

  const labelledMessages = ErrorMessageHandler.toLabelledErrorMessages(
    clientErrors,
    mergedLabels
  );
  // console.log("FormFeedback rendering labelledMessages:", labelledMessages);
  const listErrors = Object.entries(labelledMessages).map(([label, messages]) => (
    <Message.Item key={label}>
      <b>{label}</b>: {renderErrorMessages(messages)}
    </Message.Item>
  ));

  return !message ? null : (
    <Message
      id="deposit-form-feedback"
      visible
      positive={feedback === "positive"}
      warning={feedback === "warning"}
      negative={feedback === "negative"}
      className="flashed top attached icon-pulled-left pt-10"
      icon={feedback === "positive" ? "check circle outline" : "warning circle"}
      header={message}
      content={listErrors.length > 0 && <Message.List className="pt-10 pb-10">{listErrors}</Message.List>}
    ></Message>
  );
};

DisconnectedFormFeedback.propTypes = {
  errors: PropTypes.object,
  actionState: PropTypes.string,
  labels: PropTypes.object,
  clientErrors: PropTypes.object,
  nonValidationErrors: PropTypes.object,
};

DisconnectedFormFeedback.defaultProps = {
  errors: undefined,
  actionState: undefined,
  labels: undefined,
  clientErrors: undefined,
  nonValidationErrors: undefined,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  errors: state.deposit.errors,
});

const FormFeedback = connect(mapStateToProps, null)(DisconnectedFormFeedback);

export { ErrorMessageHandler, FormFeedback, defaultFieldLabels };
