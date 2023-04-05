/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { InvenioCommunitiesRoutesGenerator } from "../../../routes/appUrls";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { withState } from "react-searchkit";
import { Button, Container, Modal, Tab } from "semantic-ui-react";
import { InvitationsContext } from "../../../api/invitations/InvitationsContextProvider";
import { GroupTabPane } from "./GroupTabPane";
import { MembersWithRoleSelection } from "./MembersWithRoleSelection";

export class InvitationsMembersModal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      activeIndex: 0, // by default members is the active pane
    };
  }

  static contextType = InvitationsContext;

  onMemberSuccess = () => {
    const { updateQueryState, currentQueryState } = this.props;
    updateQueryState(currentQueryState);
    this.handleCloseModal();
  };

  onGroupSuccess = () => {
    const { community } = this.props;
    window.location = InvenioCommunitiesRoutesGenerator.membersList(community.slug);
  };

  getPanes = () => {
    const { groupsEnabled, rolesCanInvite } = this.props;
    const { api } = this.context;
    const userRoles = rolesCanInvite["user"];
    const peopleTab = {
      menuItem: i18next.t("People"),
      pane: (
        <Tab.Pane key="members-users" as={Container}>
          <MembersWithRoleSelection
            key="members-users"
            roleOptions={userRoles}
            modalClose={this.handleCloseModal}
            action={api.createInvite}
            onSuccessCallback={this.onMemberSuccess}
          />
        </Tab.Pane>
      ),
    };

    const groupRoles = rolesCanInvite["group"];
    const groupsTab = {
      menuItem: i18next.t("Groups"),
      pane: (
        <Tab.Pane key="members-groups" as={Container}>
          <GroupTabPane
            modalClose={this.handleCloseModal}
            roleOptions={groupRoles}
            action={api.addGroupToMembers}
            onSuccessCallback={this.onGroupSuccess}
          />
        </Tab.Pane>
      ),
      action: { label: i18next.t("Invite groups") },
    };
    return groupsEnabled ? [peopleTab, groupsTab] : [peopleTab];
  };

  handleCloseModal = () => this.setState({ open: false });

  handleOpenModal = () => this.setState({ open: true });

  handleTabChange = (e, { activeIndex }) => this.setState({ activeIndex });

  render() {
    const { open, activeIndex } = this.state;
    return (
      <Modal
        role="dialog"
        onClose={this.handleCloseModal}
        onOpen={this.handleOpenModal}
        closeOnDimmerClick={false}
        open={open}
        trigger={
          <Button
            className="fluid-responsive"
            content={i18next.t("Invite members")}
            positive
            size="medium"
            aria-expanded={open}
            aria-haspopup="dialog"
          />
        }
      >
        <Modal.Header as="h2">
          {activeIndex === 0 ? i18next.t("Invite members") : i18next.t("Add groups")}
        </Modal.Header>
        <Tab
          menu={{
            className: "rel-pl-2 rel-pt-2",
            tabular: true,
          }}
          activeIndex={activeIndex}
          panes={this.getPanes()}
          renderActiveOnly={false}
          onTabChange={this.handleTabChange}
        />
      </Modal>
    );
  }
}

InvitationsMembersModal.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  rolesCanInvite: PropTypes.object.isRequired,
  groupsEnabled: PropTypes.bool.isRequired,
  community: PropTypes.object.isRequired,
};

export const InvitationsMembersModalWithSearchKit = withState(InvitationsMembersModal);
