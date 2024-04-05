/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import React, { Component } from "react";
import Overridable from "react-overridable";
import { Button, Modal } from "semantic-ui-react";
import { ErrorMessage } from "./ErrorMessage";
import { ModalContext } from "./modal_manager";

export const modalModeEnum = {
  leave: 1,
  remove: 2,
};

class RemoveMemberModal extends Component {
  constructor(props) {
    super(props);

    this.state = {
      error: "",
      loading: false,
    };

    this.contentMap = {
      [modalModeEnum.leave]: {
        headerText: i18next.t("Leave community"),
        bodyText: i18next.t("You are about to leave this community."),
        buttonText: i18next.t("Leave"),
        buttonIcon: "log out",
      },
      [modalModeEnum.remove]: {
        headerText: i18next.t("Remove user"),
        bodyText: i18next.t("You are about to remove this user from this community."),
        buttonText: i18next.t("Remove"),
        buttonIcon: "user delete",
      },
    };
  }

  static contextType = ModalContext;

  onActionHandler = async () => {
    const { modalAction } = this.context;

    this.setState({ loading: true });

    try {
      await modalAction();
      this.onCloseHandler();
      window.location.reload();
    } catch (error) {
      this.setState({ error: error, loading: false });
    }
  };

  onCloseHandler = () => {
    const { closeModal } = this.context;

    this.setState({ error: "", loading: false }, () => closeModal());
  };

  render() {
    const { loading, error } = this.state;
    const { modalOpen, modalMode } = this.context;

    const content = this.contentMap[modalMode];

    return (
      <Overridable
        id="InvenioCommunities.RemoveMemberModal.layout"
        modalOpen={modalOpen}
        modalMode={modalMode}
        modalAction={this.onActionHandler}
        closeModal={this.onCloseHandler}
        contentMap={this.contentMap}
      >
        <Modal open={modalOpen} role="dialog" aria-label={i18next.t("Remove user")}>
          <Modal.Header>{content?.headerText}</Modal.Header>
          <Modal.Content>
            {content?.bodyText} <br />
            <b>{i18next.t("This action cannot be undone.")}</b>
            {error && <ErrorMessage error={error} />}
          </Modal.Content>
          <Modal.Actions>
            <Button
              content={i18next.t("Cancel")}
              loading={loading}
              onClick={this.onCloseHandler}
              floated="left"
              icon="cancel"
              labelPosition="left"
            />
            <Button
              negative
              content={content?.buttonText}
              loading={loading}
              onClick={this.onActionHandler}
              icon={content?.buttonIcon}
              labelPosition="left"
            />
          </Modal.Actions>
        </Modal>
      </Overridable>
    );
  }
}

export default Overridable.component("RemoveMemberModal", RemoveMemberModal);
