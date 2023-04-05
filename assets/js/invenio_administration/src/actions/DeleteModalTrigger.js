// This file is part of InvenioAdministration
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_administration/i18next";
import { Button, Icon } from "semantic-ui-react";
import DeleteModal from "./DeleteModal";
import { Modal } from "semantic-ui-react";
import { Trans } from "react-i18next";
import _get from "lodash/get";
import Overridable from "react-overridable";

export class DeleteModalTrigger extends Component {
  constructor(props) {
    super(props);
    this.state = { modalOpen: false };
  }

  toggleModal = (open) => {
    this.setState({ modalOpen: open });
  };

  render() {
    const {
      title,
      resourceName,
      apiEndpoint,
      resource,
      successCallback,
      idKeyPath,
      Element,
      disabled,
      disabledDeleteMessage,
    } = this.props;
    const { modalOpen } = this.state;
    const triggerId = `delete-modal-trigger-${resource.id}`;
    return (
      <Overridable id="InvenioAdministration.DeleteModalTrigger">
        <>
          <Element
            id={triggerId}
            disabled={disabled}
            icon
            negative
            onClick={() => this.toggleModal(true)}
            aria-label={i18next.t("Delete")}
            aria-controls="delete-modal"
            aria-expanded={modalOpen}
            aria-haspopup="dialog"
            title={disabledDeleteMessage}
          >
            <Icon name="trash alternate" />
          </Element>
          <DeleteModal
            id="delete-modal"
            aria-labelledby={triggerId}
            title={title}
            apiEndpoint={apiEndpoint}
            resource={resource}
            successCallback={successCallback}
            idKeyPath={idKeyPath}
            toggleModal={this.toggleModal}
            modalOpen={modalOpen}
          >
            <Modal.Content>
              <Modal.Description>
                <Trans
                  defaults="Are you sure you want to delete {{resourceName}}? "
                  values={{ resourceName: _get(resource, resourceName) }}
                />
              </Modal.Description>
            </Modal.Content>
          </DeleteModal>
        </>
      </Overridable>
    );
  }
}

DeleteModalTrigger.propTypes = {
  title: PropTypes.string.isRequired,
  resourceName: PropTypes.string.isRequired,
  apiEndpoint: PropTypes.string.isRequired,
  resource: PropTypes.object.isRequired,
  successCallback: PropTypes.func.isRequired,
  Element: PropTypes.object,
  idKeyPath: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  disabledDeleteMessage: PropTypes.string,
};

DeleteModalTrigger.defaultProps = {
  Element: Button,
  disabled: false,
  disabledDeleteMessage: "",
};
