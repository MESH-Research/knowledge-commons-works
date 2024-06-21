/*
 * This file is part of Invenio.
 * Copyright (C) 2023 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import React, { Component } from "react";
import {
  Button,
  Icon,
  Loader,
  Modal,
  Message,
  Checkbox,
  Input,
} from "semantic-ui-react";
import PropTypes from "prop-types";
import { Trans } from "react-i18next";
import { communityErrorSerializer } from "../../api/serializers";
import { ErrorMessage, http, withCancel } from "react-invenio-forms";

export class DeleteCommunityModal extends Component {
  constructor(props) {
    super(props);
    this.INITIAL_STATE = {
      modalOpen: false,
      loading: true,
      checkboxMembers: false,
      checkboxRecords: false,
      checkboxSlug: false,
      inputSlug: "",
      error: undefined,
    };
    this.checkboxRef = React.createRef();
    this.openModalBtnRef = React.createRef();
    this.state = this.INITIAL_STATE;
  }

  componentDidMount() {
    this.updateCommunityMetrics();
  }

  componentDidUpdate(prevProps, prevState) {
    const { loading, modalOpen } = this.state;
    if (!loading && modalOpen && modalOpen !== prevState.modalOpen) {
      const {
        current: { inputRef },
      } = this.checkboxRef;
      inputRef.current.focus();
    }
  }

  componentWillUnmount() {
    this.cancellableDelete && this.cancellableDelete.cancel();
    this.cancellableMembersCountFetch && this.cancellableMembersCountFetch.cancel();
    this.cancellableRecordsCountFetch && this.cancellableRecordsCountFetch.cancel();
  }

  updateCommunityMetrics = async () => {
    this.setState({ loading: true });
    const { community } = this.props;
    this.cancellableMembersCountFetch = withCancel(http.get(community.links.members));
    this.cancellableRecordsCountFetch = withCancel(http.get(community.links.records));

    try {
      const membersResponse = await this.cancellableMembersCountFetch.promise;
      const recordsResponse = await this.cancellableRecordsCountFetch.promise;
      this.setState({
        loading: false,
        membersCount: membersResponse.data.hits.total,
        recordsCount:
          recordsResponse.data.length === 0 ? 0 : recordsResponse.data.hits.total,
      });
    } catch (error) {
      console.error(error);
      const { message } = communityErrorSerializer(error);
      if (message) {
        this.setState({ error: message, loading: false });
      }
    }
  };

  handleInputChange = (event) => {
    this.setState({ inputSlug: event.target.value });
  };

  handleCheckboxChange = (e, { id, checked }) => {
    if (id === "members-confirm") {
      this.setState({
        checkboxMembers: checked,
      });
    }
    if (id === "records-confirm") {
      this.setState({
        checkboxRecords: checked,
      });
    }
    if (id === "slug-confirm") {
      this.setState({
        checkboxSlug: checked,
      });
    }
  };

  handleButtonDisabled = (slug) => {
    const { checkboxRecords, checkboxMembers, checkboxSlug, inputSlug } = this.state;
    return !(checkboxMembers && checkboxRecords && checkboxSlug && inputSlug === slug);
  };

  openConfirmModal = () => this.setState({ modalOpen: true });

  closeConfirmModal = () => {
    let { loading } = this.state;
    this.setState({ ...this.INITIAL_STATE, loading: loading });
    this.openModalBtnRef?.current?.focus();
  };

  handleDelete = async () => {
    this.setState({ loading: true });
    const { onDelete, redirectURL } = this.props;

    this.cancellableDelete = withCancel(onDelete());
    try {
      await this.cancellableDelete.promise;

      if (redirectURL) {
        window.location.href = redirectURL;
      }

      this.closeConfirmModal();
    } catch (error) {
      if (error === "UNMOUNTED") return;
      console.error(error);
      const { message } = communityErrorSerializer(error);
      if (message) {
        this.setState({ error: message, loading: false });
      }
    }
  };

  render() {
    const {
      modalOpen,
      loading,
      error,
      checkboxMembers,
      checkboxRecords,
      checkboxSlug,
      inputSlug,
      membersCount,
      recordsCount,
    } = this.state;
    const { label, community } = this.props;
    const communitySlug = community.slug;
    return (
      <>
        <Button
          ref={this.openModalBtnRef}
          compact
          negative
          onClick={this.openConfirmModal}
          fluid
          icon
          labelPosition="left"
          type="button"
          aria-haspopup="dialog"
          aria-controls="warning-modal"
          aria-expanded={modalOpen}
          id="delete-community-button"
        >
          <Icon name="trash" />
          {label}
        </Button>

        <Modal
          id="warning-modal"
          role="dialog"
          aria-labelledby="delete-community-button"
          open={modalOpen}
          onClose={this.closeConfirmModal}
          size="tiny"
        >
          <Modal.Header as="h2">
            {i18next.t("Permanently delete community")}
          </Modal.Header>
          {loading && <Loader active={loading} />}
          <Modal.Content>
            <p>
              <Trans>
                Are you <strong>absolutely sure</strong> you want to delete the
                community?
              </Trans>
            </p>

            <Message negative>
              <Message.Header className="rel-mb-1">
                <Icon name="warning sign" className="rel-mr-1" />
                {i18next.t("This action CANNOT be undone!")}
              </Message.Header>
              <>
                <Checkbox
                  id="members-confirm"
                  ref={this.checkboxRef}
                  label={
                    <label htmlFor="members-confirm">
                      <Trans>
                        <strong>{`${membersCount}`} members</strong> will be removed
                        from the community.
                      </Trans>
                    </label>
                  }
                  checked={checkboxMembers}
                  onChange={this.handleCheckboxChange}
                  className="mb-5"
                />
                <Checkbox
                  id="records-confirm"
                  label={
                    <label htmlFor="records-confirm">
                      <Trans>
                        <strong>{`${recordsCount}`} records</strong> will be removed
                        from the community.
                      </Trans>
                    </label>
                  }
                  checked={checkboxRecords}
                  onChange={this.handleCheckboxChange}
                  className="mb-5"
                />
                <Checkbox
                  id="slug-confirm"
                  label={
                    <label htmlFor="slug-confirm">
                      <Trans>
                        You <strong>CANNOT</strong> reuse the community identifier "
                        {{ communitySlug }}".
                      </Trans>
                    </label>
                  }
                  checked={checkboxSlug}
                  onChange={this.handleCheckboxChange}
                  className="mb-5"
                />
              </>
            </Message>

            <label htmlFor="confirm-delete">
              <Trans>
                Please type <strong>{{ communitySlug }}</strong> to confirm.
              </Trans>
            </label>
            <Input
              id="confirm-delete"
              fluid
              value={inputSlug}
              onChange={this.handleInputChange}
            />
          </Modal.Content>
          <Modal.Actions>
            {error && (
              <ErrorMessage
                header={i18next.t("Unable to delete")}
                content={i18next.t(error)}
                icon="exclamation"
                className="text-align-left"
                negative
              />
            )}
            <Button onClick={this.closeConfirmModal} floated="left">
              {i18next.t("Cancel")}
            </Button>
            <Button
              negative
              onClick={() => this.handleDelete()}
              disabled={this.handleButtonDisabled(communitySlug)}
            >
              {i18next.t("Permanently delete")}
            </Button>
          </Modal.Actions>
        </Modal>
      </>
    );
  }
}

DeleteCommunityModal.propTypes = {
  onDelete: PropTypes.func.isRequired,
  redirectURL: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  community: PropTypes.object.isRequired,
};
