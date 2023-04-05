/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2021 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import React, { Component } from "react";
import { withCancel } from "react-invenio-forms";
import { Button, Form, Icon, Modal } from "semantic-ui-react";
import { CommunityApi } from "../../api";
import { communityErrorSerializer } from "../../api/serializers";
import PropTypes from "prop-types";

export class RenameCommunitySlugButton extends Component {
  constructor(props) {
    super(props);

    this.state = {
      modalOpen: false,
      loading: false,
      error: "",
    };

    this.formInputRef = React.createRef();
  }

  componentWillUnmount() {
    this.cancellableRename && this.cancellableRename.cancel();
  }

  handleOpen = () => this.setState({ modalOpen: true });

  handleClose = () => this.setState({ modalOpen: false });

  handleChange = async (event) => {
    // stop event propagation so the submit event is restricted to the modal
    // form
    event.stopPropagation();
    const { community } = this.props;
    const newSlug = this.formInputRef.current.value;
    const client = new CommunityApi();

    this.cancellableRename = withCancel(client.renameSlug(community.id, newSlug));
    this.setState({ loading: true });

    try {
      await this.cancellableRename.promise;

      window.location.href = `/communities/${newSlug}/settings`;
    } catch (error) {
      if (error === "UNMOUNTED") return;

      this.setState({ loading: false });
      const { errors } = communityErrorSerializer(error);

      if (errors) {
        const invalidIdError = errors
          .filter((error) => error.field === "slug")
          .map((error) => error.messages[0]);
        this.setState({ error: invalidIdError });
      }
    }
  };

  render() {
    const { modalOpen, loading, error } = this.state;

    return (
      <>
        <Button
          compact
          negative
          onClick={this.handleOpen}
          fluid
          icon
          labelPosition="left"
          type="button"
        >
          <Icon name="pencil" />
          {i18next.t("Change identifier")}
        </Button>

        <Modal open={modalOpen} onClose={this.handleClose} size="tiny">
          <Modal.Content>
            <Form onSubmit={this.handleChange}>
              <Form.Input
                label={i18next.t("New unique identifier of the community")}
                placeholder={i18next.t("New unique identifier of the community")}
                fluid
                input={{ ref: this.formInputRef }}
                {...(error
                  ? {
                      error: {
                        content: error,
                        pointing: "above",
                      },
                    }
                  : {})}
              />
            </Form>
          </Modal.Content>
          <Modal.Actions>
            <Button
              onClick={this.handleClose}
              loading={loading}
              disabled={loading}
              floated="left"
            >
              {i18next.t("Cancel")}
            </Button>
            <Button
              negative
              onClick={this.handleChange}
              loading={loading}
              disabled={loading}
            >
              {i18next.t("Change")}
            </Button>
          </Modal.Actions>
        </Modal>
      </>
    );
  }
}

RenameCommunitySlugButton.propTypes = {
  community: PropTypes.object.isRequired,
  onError: PropTypes.func.isRequired,
};
