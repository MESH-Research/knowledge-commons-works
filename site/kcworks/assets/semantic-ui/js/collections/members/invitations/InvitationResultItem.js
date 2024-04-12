/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import { Container, Grid, Item, Table } from "semantic-ui-react";
import { InvitationsContext } from "../../api/invitations/InvitationsContextProvider";
import { RoleDropdown } from "../components/dropdowns";
import RequestStatus from "@js/invenio_requests/request/RequestStatus";

const formattedTime = (expiresAt) =>
  DateTime.fromISO(expiresAt).setLocale(i18next.language).toRelative();

export class InvitationResultItem extends Component {
  constructor(props) {
    super(props);
    const { result } = this.props;
    this.state = { invitation: result };
  }

  static contextType = InvitationsContext;

  updateInvitation = (data, value) => {
    const { invitation } = this.state;
    this.setState({ invitation: { ...invitation, ...{ role: value } } });
  };

  render() {
    const {
      config: { rolesCanInvite },
      community,
    } = this.props;
    const {
      invitation: { member, request },
      invitation,
    } = this.state;
    const { api: invitationsApi } = this.context;
    const rolesCanInviteByType = rolesCanInvite[member.type];
    const memberInvitationExpiration = formattedTime(request.expires_at);
    return (
      <Table.Row className="community-member-item">
        <Table.Cell>
          <Grid textAlign="left" verticalAlign="middle">
            <Grid.Column>
              <Item className="flex align-items-center" key={invitation.id}>
                <Image src={member.avatar} avatar circular className="mr-10" />
                <Item.Content>
                  <Item.Header size="small" as="b">
                    <a href={`/communities/${community.slug}/requests/${request.id}`}>
                      {member.name}
                    </a>
                  </Item.Header>
                  {member.description && (
                    <Item.Meta>
                      <div className="truncate-lines-1">{member.description}</div>
                    </Item.Meta>
                  )}
                </Item.Content>
              </Item>
            </Grid.Column>
          </Grid>
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Status")}>
          <RequestStatus status={request.status} />
        </Table.Cell>
        <Table.Cell
          aria-label={i18next.t("Expires") + " " + memberInvitationExpiration}
          data-label={i18next.t("Expires")}
        >
          {memberInvitationExpiration}
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Role")}>
          <RoleDropdown
            roles={rolesCanInviteByType}
            successCallback={this.updateInvitation}
            action={invitationsApi.updateRole}
            disabled={!invitation.permissions.can_update_role}
            currentValue={invitation.role}
            resource={invitation}
            label={i18next.t("Role") + " " + invitation.role}
          />
        </Table.Cell>
        <Table.Cell>
          <Container fluid textAlign="right">
            {/* TODO uncomment when links available in the request resource subschema */}
            {/*<RequestActionController*/}
            {/*  request={request }*/}
            {/*  actionSuccessCallback={this.updateInvitation}*/}
            {/*>*/}
            {/*<ActionButtons request={invitation} />*/}
            {/*</RequestActionController>*/}
          </Container>
        </Table.Cell>
      </Table.Row>
    );
  }
}

InvitationResultItem.propTypes = {
  result: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
};

InvitationResultItem.defaultProps = {};
