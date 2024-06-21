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
import { Table } from "semantic-ui-react";
import { InvitationsContextProvider } from "../../api/invitations/InvitationsContextProvider";
import { InvitationsMembersModalWithSearchKit } from "./invitationsModal/InvitationsMembersModal";

export const InvitationsResultsContainer = ({
  results,
  rolesCanInvite,
  community,
  communityGroupsEnabled,
}) => {
  return (
    <Table>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell width={6}>{i18next.t("Name")}</Table.HeaderCell>
          <Table.HeaderCell width={3}>{i18next.t("Status")}</Table.HeaderCell>
          <Table.HeaderCell width={3}>{i18next.t("Expires")}</Table.HeaderCell>
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

InvitationsResultsContainer.propTypes = {
  results: PropTypes.array.isRequired,
  rolesCanInvite: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  communityGroupsEnabled: PropTypes.bool.isRequired,
};
