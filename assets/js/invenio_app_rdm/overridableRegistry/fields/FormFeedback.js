// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import _isObject from "lodash/isObject";
import _merge from "lodash/merge";
import React, { Component } from "react";
import { connect } from "react-redux";
import { Grid, Icon, Message } from "semantic-ui-react";
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

const readableMessageEquivalents = {
  "Missing data for required field.": "Missing a value for a required field.",
  "Field may not be null.": "Field cannot be empty.",
};

const defaultLabels = {
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
  "pids": i18next.t("DOI"),
};

const ACTIONS = {
  ["CLIENT_VALIDATION_ERRORS"]: {
    feedback: "negative",
    message: i18next.t("Please correct the errors in the form."),
  },
  [DRAFT_SAVE_SUCCEEDED]: {
    feedback: "positive",
    message: i18next.t("Draft successfully saved."),
  },
  [DRAFT_HAS_VALIDATION_ERRORS]: {
    feedback: "warning",
    message: i18next.t(
      "Draft saved, but some field values could not be accepted:"
    ),
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
    const readableEquivalents = {
      "Missing data for required field.": "Missing a value for a required field.",
      "Field may not be null.": "Field cannot be empty.",
    };
    if (readableEquivalents[error]) {
      return readableEquivalents[error];
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
    const metadata = Object.entries(errors.metadata || {}).map(([key, value]) => {
      return ["metadata." + key, value];
    });
    const files = Object.entries(errors.files || {}).map(([key, value]) => {
      return ["files." + key, value];
    });
    const access = Object.entries(errors?.access || {}).map(([key, value]) => {
      return ["access.embargo." + key, value];
    });
    const pids = _isObject(errors.pids)
      ? Object.entries(errors.pids || {}).map(([key, value]) => {
          return ["pids." + key, value];
        })
      : [["pids", errors.pids || {}]];
    const customFields = Object.entries(errors.customFields || {}).map(
      ([key, value]) => {
        return ["custom_fields." + key, value];
      }
    );
    const collapsedErrors = Object.fromEntries(
      metadata.concat(files).concat(access).concat(pids).concat(customFields)
    );
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
      const label = labels[key] || "Unknown field";
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

class DisconnectedFormFeedback extends Component {
  constructor(props) {
    super(props);
    this.labels = {
      ...defaultLabels,
      ...props.labels,
    };
  }

  /**
   * Render error messages inline (if 1) or as list (if multiple).
   *
   * @param {Array<String>} messages
   * @returns String or React node
   */
  renderErrorMessages(messages) {
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
  }

  render() {
    const { errors: errorsProp, actionState, clientErrors, clientInitialErrors, clientInitialValues, ...rest } = this.props;

    // Merge client-side validation errors with backend errors
    console.log("FormFeedback errorsProp:", errorsProp);
    console.log("FormFeedback clientErrors:", clientErrors);
    console.log("FormFeedback actionState:", actionState);
    console.log("FormFeedback rest:", rest);
    console.log("FormFeedback labels:", this.labels, this.props.labels, defaultLabels)

    const errors = errorsProp
      ? _merge(errorsProp, clientErrors)
      : clientErrors
      ? clientErrors
      : {};

    const combinedActionState =
      !_isEmpty(clientErrors) ? "CLIENT_VALIDATION_ERRORS" : actionState;

    const { feedback, message } = _get(ACTIONS, combinedActionState, {
      feedback: undefined,
      message: undefined,
    });

    if (!message) {
      // if no message to display, simply return null
      return null;
    }

    const labelledMessages = ErrorMessageHandler.toLabelledErrorMessages(errors, this.labels);
    const listErrors = Object.entries(labelledMessages).map(
      ([label, messages]) => (
        <Message.Item key={label}>
          <b>{label}</b>: {this.renderErrorMessages(messages)}
        </Message.Item>
      )
    );

    // errors not related to validation, following a different format {status:.., message:..}
    const backendErrorMessage = errors.message;

    return (
      <Message
        id="deposit-form-feedback"
        visible
        positive={feedback === "positive"}
        warning={feedback === "warning"}
        negative={feedback === "negative"}
        className="flashed top attached"
        icon={
          feedback === "positive" ? "check circle outline" : "warning circle"
        }
        header={backendErrorMessage || message}
        content={
          listErrors.length > 0 && <Message.List>{listErrors}</Message.List>
        }
      ></Message>
    );
  }
}

DisconnectedFormFeedback.propTypes = {
  errors: PropTypes.object,
  actionState: PropTypes.string,
  labels: PropTypes.object,
};

DisconnectedFormFeedback.defaultProps = {
  errors: undefined,
  actionState: undefined,
  labels: undefined,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  errors: state.deposit.errors,
});

export const FormFeedback = connect(
  mapStateToProps,
  null
)(DisconnectedFormFeedback);

export { ErrorMessageHandler };