// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
//
// Customized for Knowledge Commons Works
// Copyright (C) 2024 Mesh Research
//
// Invenio-RDM-Records and Knowledge Commons Works are free software;
// you can redistribute and/or modify them under the terms of the MIT License;
// see LICENSE file for more details.

import { i18next } from "@translations/invenio_modular_deposit_form/i18next";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";
import { Button, Header, Modal } from "semantic-ui-react";
import { CommunityContext } from "@js/invenio_rdm_records/src/deposit/components/CommunitySelectionModal/CommunityContext";
import { CommunitySelectionSearch } from "./CommunitySelectionSearch";

export class CommunitySelectionModalComponent extends Component {
  constructor(props) {
    super(props);
    const { chosenCommunity, userCommunitiesMemberships, displaySelected } = props;

    this.state = {
      localChosenCommunity: chosenCommunity,
    };

    this.contextValue = {
      setLocalCommunity: this.setCommunity,
      getChosenCommunity: this.getChosenCommunity,
      userCommunitiesMemberships,
      displaySelected,
    };
  }

  getChosenCommunity = () => {
    const { localChosenCommunity } = this.state;
    return localChosenCommunity;
  };

  setCommunity = (community) => {
    const { onCommunityChange } = this.props;
    onCommunityChange(community);
    this.setState({ localChosenCommunity: community });
  };

  modalTrigger = () => {
    const { trigger, modalOpen } = this.props;
    if (!_isEmpty(trigger)) {
      return React.cloneElement(trigger, {
        "aria-haspopup": "dialog",
        "aria-expanded": modalOpen,
      });
    }
  };

  handleModalOpen = () => {
    const { chosenCommunity, onModalChange } = this.props;
    this.setState({ localChosenCommunity: chosenCommunity });
    onModalChange && onModalChange(true);
  };

  render() {
    const {
      extraContentComponents,
      modalHeader,
      onModalChange,
      modalOpen,
      apiConfigs,
      record,
      isInitialSubmission,
      permissionsPerField,
    } = this.props;

    return (
      <CommunityContext.Provider value={this.contextValue}>
        <Modal
          role="dialog"
          aria-labelledby="community-modal-header"
          id="community-selection-modal"
          className="m-0"
          closeIcon
          closeOnDimmerClick={false}
          open={modalOpen}
          onClose={() => {
            onModalChange && onModalChange(false);
          }}
          onOpen={this.handleModalOpen}
          trigger={this.modalTrigger()}
        >
          <Modal.Header className="pb-15 pt-25">
            <Header as="h2" id="community-modal-header">
              {modalHeader}
            </Header>
          </Modal.Header>

          <CommunitySelectionSearch
            apiConfigs={apiConfigs}
            record={record}
            isInitialSubmission={isInitialSubmission}
            permissionsPerField={permissionsPerField}
          />
          {extraContentComponents && (
            <Modal.Content>{extraContentComponents}</Modal.Content>
          )}

          <Modal.Actions>
            <Button onClick={() => onModalChange(false)}>{i18next.t("Close")}</Button>
          </Modal.Actions>
        </Modal>
      </CommunityContext.Provider>
    );
  }
}

CommunitySelectionModalComponent.propTypes = {
  chosenCommunity: PropTypes.object,
  onCommunityChange: PropTypes.func.isRequired,
  trigger: PropTypes.object,
  userCommunitiesMemberships: PropTypes.object.isRequired,
  extraContentComponents: PropTypes.node,
  modalHeader: PropTypes.string,
  onModalChange: PropTypes.func,
  displaySelected: PropTypes.bool,
  modalOpen: PropTypes.bool,
  apiConfigs: PropTypes.object,
  handleClose: PropTypes.func.isRequired,
  record: PropTypes.object,
  isInitialSubmission: PropTypes.bool,
  permissionsPerField: PropTypes.object,
};

CommunitySelectionModalComponent.defaultProps = {
  chosenCommunity: undefined,
  extraContentComponents: undefined,
  modalHeader: undefined,
  onModalChange: undefined,
  displaySelected: false,
  modalOpen: false,
  trigger: undefined,
  apiConfigs: undefined,
  isInitialSubmission: true,
  permissionsPerField: undefined,
};

const mapStateToProps = (state) => ({
  userCommunitiesMemberships: state.deposit.config.user_communities_memberships,
});

export const CommunitySelectionModal = connect(
  mapStateToProps,
  null
)(CommunitySelectionModalComponent);
