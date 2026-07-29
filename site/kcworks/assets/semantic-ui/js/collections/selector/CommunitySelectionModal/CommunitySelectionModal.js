// This file is part of Knowledge-Commons-Works
// Copyright (C) 2024-2026 Mesh Research
//
// Adapted from a component in Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
//
// Invenio-RDM-Records and Knowledge Commons Works are free software;
// you can redistribute and/or modify them under the terms of the MIT License;
// see LICENSE file for more details.

import React, { useEffect, useState } from "react";
import { i18next } from "@translations/invenio_modular_deposit_form/i18next";
import { Trans } from "react-i18next";
import PropTypes from "prop-types";
import { useStore } from "react-redux";
import { Button, Header, Modal } from "semantic-ui-react";
import { CommunityContext } from "@js/invenio_rdm_records/src/deposit/components/CommunitySelectionModal/CommunityContext";
import { CommunitySelectionSearch } from "./CommunitySelectionSearch";

const SubmissionWarningModal = ({ open = false, onCancel, onAccept }) => {
  return (
    <Modal
      className="deposit-publication-review-warning"
      open={open}
      onClose={onCancel}
      closeOnDimmerClick={false}
      small
    >
      <Modal.Header>
        <Trans
          defaults="You may want to submit to collections <0>after</0> your work is published"
          components={[<i />]}
        />
      </Modal.Header>
      <Modal.Content>
        <p>
          <Trans
            defaults="Submitting to a collection is optional. If you submit your work for publication by a collection now, your upload <0>will not be publicly visible</0> until it has been approved by that collection's curators."
            components={[<b />]}
          />
        </p>
        <p>
          <Trans
            defaults="Most collections are <0>not curated by the KCWorks team</0> , and collection curators may take a significant amount of time to review your work."
            components={[<b />]}
          />
        </p>
        <p>
          <Trans
            defaults="You can submit your work to a collection <0>after publication</0> from the sidebar of your published record's detail page"
            components={[<b />]}
          />
        </p>
      </Modal.Content>
      <Modal.Actions>
        <Button onClick={onCancel}>{i18next.t("Cancel")}</Button>
        <Button positive onClick={onAccept}>
          {i18next.t("Choose a collection")}
        </Button>
      </Modal.Actions>
    </Modal>
  );
};

const CommunitySelectionModal = ({
  apiConfigs = undefined,
  chosenCommunity = undefined,
  displaySelected = false,
  extraContentComponents = undefined,
  isInitialSubmission = true,
  modalHeader = undefined,
  modalOpen = false,
  onCommunityChange = undefined,
  onModalChange = undefined,
  permissionsPerField = undefined,
  record = {},
  setModalOpen = undefined,
  showSubmissionWarning = false,
  trigger = undefined,
  ...restProps
}) => {
  const state = useStore().getState();
  const userCommunitiesMemberships = state.deposit.config.user_communities_memberships;
  const [localChosenCommunity, setLocalChosenCommunity] = useState(chosenCommunity);
  const [warningOpen, setWarningOpen] = useState(false);
  const [warningSeen, setWarningSeen] = useState(false);

  const getChosenCommunity = () => {
    return localChosenCommunity;
  };

  const setCommunity = (community) => {
    onCommunityChange(community);
    setLocalChosenCommunity(community);
  };

  const contextValue = {
    setLocalCommunity: setCommunity,
    getChosenCommunity: getChosenCommunity,
    userCommunitiesMemberships,
    displaySelected,
  };

  // Button onClick sets modalOpen; Modal onOpen does not fire with Overridable as
  // trigger root. Open the warning from controlled open state instead.
  useEffect(() => {
    console.log("modalOpen", modalOpen);
    console.log("showSubmissionWarning", showSubmissionWarning);
    console.log("warningSeen", warningSeen);
    if (modalOpen && showSubmissionWarning && !warningSeen) {
      console.log("opening warning");
      setWarningOpen(true);
    }
  }, [modalOpen, showSubmissionWarning, warningSeen]);

  const handleModalOpen = () => {
    setLocalChosenCommunity(chosenCommunity);
    onModalChange && onModalChange(true);
  };

  return (
    <>
      <CommunityContext.Provider value={contextValue}>
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
          onOpen={handleModalOpen}
          trigger={trigger}
          {...restProps}
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
          {extraContentComponents && <Modal.Content>{extraContentComponents}</Modal.Content>}

          <Modal.Actions>
            <Button onClick={() => onModalChange(false)}>{i18next.t("Close")}</Button>
          </Modal.Actions>
        </Modal>
      </CommunityContext.Provider>
      <SubmissionWarningModal
        open={warningOpen}
        onCancel={() => {
          setWarningSeen(true);
          setWarningOpen(false);
          onModalChange && onModalChange(false);
        }}
        onAccept={() => {
          setWarningSeen(true);
          setWarningOpen(false);
          onModalChange && onModalChange(true);
        }}
      />
    </>
  );
};

CommunitySelectionModal.propTypes = {
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
  setModalOpen: PropTypes.func,
  showSubmissionWarning: PropTypes.bool,
};

export { CommunitySelectionModal };
