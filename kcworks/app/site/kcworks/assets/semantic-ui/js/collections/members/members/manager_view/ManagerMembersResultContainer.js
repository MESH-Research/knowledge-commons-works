/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import { i18next } from "@translations/invenio_communities/i18next";
import React from "react";
import PropTypes from "prop-types";
import { InvitationsContextProvider } from "../../../api/invitations/InvitationsContextProvider";
import { InvitationsMembersModalWithSearchKit } from "../../invitations/invitationsModal/InvitationsMembersModal";
import { Table } from "semantic-ui-react";
import { ManagerMemberBulkActions } from "./ManagerMemberBulkActions";

export const ManagerMembersResultsContainer = ({
  results,
  community,
  communityGroupsEnabled,
  rolesCanInvite,
  config,
}) => {
  return (
    <Table>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell width={6}>
            <ManagerMemberBulkActions
              community={community}
              roles={config.roles}
              visibilities={config.visibility}
              permissions={config.permissions}
            />
          </Table.HeaderCell>
          <Table.HeaderCell width={3}>{i18next.t("Member since")}</Table.HeaderCell>
          <Table.HeaderCell width={3}>{i18next.t("Visibility")}</Table.HeaderCell>
          <Table.HeaderCell width={3}>{i18next.t("Role")}</Table.HeaderCell>
          <Table.HeaderCell width={1} textAlign="right">
            <InvitationsContextProvider community={community}>
              <InvitationsMembersModalWithSearchKit
                rolesCanInvite={rolesCanInvite}
                groupsEnabled={communityGroupsEnabled}
                community={community}
                triggerButtonSize="tiny"
              />
            </InvitationsContextProvider>
          </Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>{results}</Table.Body>
    </Table>
  );
};

ManagerMembersResultsContainer.propTypes = {
  results: PropTypes.array.isRequired,
  community: PropTypes.object.isRequired,
  rolesCanInvite: PropTypes.object.isRequired,
  communityGroupsEnabled: PropTypes.bool.isRequired,
  config: PropTypes.object.isRequired,
};
