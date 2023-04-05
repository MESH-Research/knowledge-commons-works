// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import React, { Component } from "react";
import { Modal, Button, Message } from "semantic-ui-react";
import PropTypes from "prop-types";

export const BaseModal = ({
  contentText,
  action,
  isLoading,
  error,
  headerText,
  cancelButtonText,
  actionButtonText,
  open,
  onOpen,
  onClose,
}) => {
  return (
    <Modal onClose={onOpen} onOpen={onClose} open={open}>
      <Modal.Header>{headerText}</Modal.Header>
      <Modal.Content>{contentText}</Modal.Content>
      <Modal.Actions>
        {error && (
          <Message negative compact>
            {error}
          </Message>
        )}

        <Button content={cancelButtonText} onClick={() => onClose()} />
        <Button
          content={actionButtonText}
          negative
          onClick={() => action()}
          loading={isLoading}
        />
      </Modal.Actions>
    </Modal>
  );
};

BaseModal.propTypes = {
  contentText: PropTypes.string.isRequired,
  action: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  error: PropTypes.string.isRequired,
  headerText: PropTypes.string.isRequired,
  cancelButtonText: PropTypes.string.isRequired,
  actionButtonText: PropTypes.string.isRequired,
};

export default BaseModal;
