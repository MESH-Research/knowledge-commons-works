/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2021 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import React, { useEffect, useState } from "react";
import { Button, Icon, Modal } from "semantic-ui-react";
import PropTypes from "prop-types";

export const DeleteButton = (props) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const cancelBtnRef = React.createRef();
  const openModalBtnRef = React.createRef();

  const handleOpen = () => setModalOpen(true);

  const handleClose = () => {
    setModalOpen(false);
    setLoading(false);
    openModalBtnRef?.current?.focus();
  };

  const handleDelete = async () => {
    setLoading(true);
    const { onDelete, redirectURL, onError } = props;
    try {
      await onDelete();
      if (redirectURL) {
        window.location.href = redirectURL;
      }
    } catch (error) {
      onError(error);
    }
    handleClose();
  };

  useEffect(() => {
    if (modalOpen) cancelBtnRef?.current?.focus();
  }, [modalOpen, cancelBtnRef]);

  const { label, confirmationMessage, id } = props;

  return (
    <>
      <Button
        ref={openModalBtnRef}
        compact
        negative
        onClick={handleOpen}
        fluid
        icon
        labelPosition="left"
        type="button"
        aria-haspopup="dialog"
        aria-controls="warning-modal"
        aria-expanded={modalOpen}
        id={id}
      >
        <Icon name="trash" />
        {label}
      </Button>

      <Modal
        id="warning-modal"
        role="dialog"
        aria-labelledby={id}
        open={modalOpen}
        onClose={handleClose}
        size="tiny"
      >
        <Modal.Content>{confirmationMessage}</Modal.Content>
        <Modal.Actions>
          <Button
            ref={cancelBtnRef}
            onClick={handleClose}
            loading={loading}
            floated="left"
          >
            {i18next.t("Cancel")}
          </Button>
          <Button negative onClick={handleDelete} loading={loading}>
            {i18next.t("Delete")}
          </Button>
        </Modal.Actions>
      </Modal>
    </>
  );
};

DeleteButton.propTypes = {
  onDelete: PropTypes.func.isRequired,
  redirectURL: PropTypes.string.isRequired,
  onError: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
  confirmationMessage: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
};
