/*
 * // This file is part of Invenio-App-Rdm
 * // Copyright (C) 2023 CERN.
 * //
 * // Invenio-App-Rdm is free software; you can redistribute it and/or modify it
 * // under the terms of the MIT License; see LICENSE file for more details.
 */

import { RestoreConfirmation } from "./RestoreConfirmation";
import TombstoneForm from "./TombstoneForm";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Modal, Icon } from "semantic-ui-react";
import { ActionModal, ActionForm } from "@js/invenio_administration";
import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/invenio_app_rdm/i18next";

export class RecordResourceActions extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    };
  }

  onModalTriggerClick = (e, { payloadSchema, dataName, dataActionKey }) => {
    const { resource } = this.props;

    if (dataActionKey === "delete") {
      this.setState({
        modalOpen: true,
        modalHeader: i18next.t("Delete community"),
        modalBody: (
          <TombstoneForm
            actionSuccessCallback={this.handleSuccess}
            actionCancelCallback={this.closeModal}
            resource={resource}
          />
        ),
      });
    } else if (dataActionKey === "restore") {
      this.setState({
        modalOpen: true,
        modalHeader: i18next.t("Restore community"),
        modalBody: (
          <RestoreConfirmation
            actionSuccessCallback={this.handleSuccess}
            actionCancelCallback={this.closeModal}
            resource={resource}
          />
        ),
      });
    } else {
      this.setState({
        modalOpen: true,
        modalHeader: dataName,
        modalBody: (
          <ActionForm
            actionKey={dataActionKey}
            actionSchema={payloadSchema}
            actionSuccessCallback={this.handleSuccess}
            actionCancelCallback={this.closeModal}
            resource={resource}
          />
        ),
      });
    }
  };

  closeModal = () => {
    this.setState({
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    });
  };

  handleSuccess = () => {
    const { successCallback } = this.props;
    this.setState({
      modalOpen: false,
      modalHeader: undefined,
      modalBody: undefined,
    });
    successCallback();
  };

  render() {
    const { actions, Element, resource } = this.props;
    const { modalOpen, modalHeader, modalBody } = this.state;
    return (
      <>
        {Object.entries(actions).map(([actionKey, actionConfig]) => {
          if (actionKey === "delete" && !resource.deletion_status.is_deleted) {
            return (
              <Element
                key={actionKey}
                onClick={this.onModalTriggerClick}
                payloadSchema={actionConfig.payload_schema}
                dataName={actionConfig.text}
                dataActionKey={actionKey}
                icon
                fluid
                labelPosition="left"
              >
                <Icon name="trash alternate" />
                {actionConfig.text}
              </Element>
            );
          } else if (actionKey === "restore" && resource.deletion_status.is_deleted) {
            return (
              <Element
                key={actionKey}
                onClick={this.onModalTriggerClick}
                payloadSchema={actionConfig.payload_schema}
                dataName={actionConfig.text}
                dataActionKey={actionKey}
                icon
                fluid
                labelPosition="left"
              >
                <Icon name="undo" />
                {actionConfig.text}
              </Element>
            );
          } else if (!resource.deletion_status.is_deleted && actionKey !== "restore") {
            return (
              <Element
                key={actionKey}
                onClick={this.onModalTriggerClick}
                payloadSchema={actionConfig.payload_schema}
                dataName={actionConfig.text}
                dataActionKey={actionKey}
              >
                {actionConfig.text}
              </Element>
            );
          }
        })}
        <ActionModal modalOpen={modalOpen} resource={resource}>
          {modalHeader && <Modal.Header>{modalHeader}</Modal.Header>}
          {!_isEmpty(modalBody) && modalBody}
        </ActionModal>
      </>
    );
  }
}

RecordResourceActions.propTypes = {
  resource: PropTypes.object.isRequired,
  successCallback: PropTypes.func.isRequired,
  actions: PropTypes.shape({
    text: PropTypes.string.isRequired,
    payload_schema: PropTypes.object.isRequired,
    order: PropTypes.number.isRequired,
  }),
  Element: PropTypes.node,
};

RecordResourceActions.defaultProps = {
  Element: Button,
  actions: undefined,
};
