/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import { SelectedMembers } from "@js/invenio_communities/members/components/bulk_actions/SelectedMembers";
import { RadioSelection } from "@js/invenio_communities/members/components/bulk_actions/RadioSelection";
import { ErrorMessage } from "@js/invenio_communities/members/components/ErrorMessage";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { Modal, Form, Button } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { MembersSearchBar } from "./MemberSearchBar";
import { GroupsApi } from "../../../api/GroupsApi";
import { Trans } from "react-i18next";
import { RichEditor } from "react-invenio-forms";

export class GroupTabPane extends Component {
  constructor(props) {
    super(props);
    this.state = {
      role: undefined,
      selectedMembers: {},
      message: undefined,
      loading: false,
      error: undefined,
    };
  }

  updateSelectedMembers = (members) => {
    this.setState({ selectedMembers: members });
  };

  addMemberToSelected = (member) => {
    const { selectedMembers } = this.state;
    this.setState({ selectedMembers: { ...selectedMembers, ...member } });
  };

  handleRoleUpdate = (role) => {
    this.setState({ role: role });
  };

  handleActionClick = async () => {
    const { action, onSuccessCallback } = this.props;
    const { selectedMembers, role, message } = this.state;
    this.setState({ loading: true, error: undefined });
    try {
      await action(selectedMembers, role, message);
      this.setState({ loading: false });
      onSuccessCallback();
    } catch (error) {
      this.setState({ loading: false, error: error });
    }
  };

  render() {
    const { roleOptions, modalClose } = this.props;
    const { selectedMembers, loading, error } = this.state;
    const selectedCount = Object.keys(selectedMembers).length;

    const client = new GroupsApi();

    return (
      <>
        <div className="rel-pl-2 rel-pr-2 rel-pb-2 rel-pt-2">
          {error && <ErrorMessage error={error} />}
          <SelectedMembers
            updateSelectedMembers={this.updateSelectedMembers}
            selectedMembers={selectedMembers}
            displayingGroups
          />
          <Form>
            <Form.Field>
              <label>{i18next.t("Group")}</label>
              <MembersSearchBar
                fetchMembers={client.getGroups}
                selectedMembers={selectedMembers}
                handleChange={this.addMemberToSelected}
                searchType="group"
                placeholder={i18next.t("Search for groups")}
              />
            </Form.Field>
            <Form.Field required>
              <RadioSelection
                options={roleOptions}
                label={i18next.t("Role")}
                onOptionChangeCallback={this.handleRoleUpdate}
              />
            </Form.Field>
            <Form.Field disabled>
              <>
                <label>{i18next.t("Message")}</label>
                <RichEditor />
              </>
            </Form.Field>
          </Form>
        </div>
        <Modal.Actions>
          <Button
            content={i18next.t("Cancel")}
            labelPosition="left"
            icon="cancel"
            loading={loading}
            disabled={loading}
            floated="left"
            onClick={modalClose}
          />
          {selectedCount > 0 && (
            <Trans key="communityInviteMembersSelected" count={selectedCount}>
              You are about to add {{ selectedCount }} groups.
            </Trans>
          )}

          <Button
            content={i18next.t("Add")}
            labelPosition="left"
            loading={loading}
            disabled={loading || selectedCount === 0}
            icon="checkmark"
            primary
            onClick={this.handleActionClick}
          />
        </Modal.Actions>
      </>
    );
  }
}

GroupTabPane.propTypes = {
  roleOptions: PropTypes.array.isRequired,
  modalClose: PropTypes.func.isRequired,
  action: PropTypes.func.isRequired,
  onSuccessCallback: PropTypes.func.isRequired,
};
