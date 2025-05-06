/*
* This file is part of Knowledge Commons Works.
* Copyright (C) 2024 Mesh Research.
*
* Knowledge Commons Works is based on InvenioRDM, and
* this file is based on code from InvenioRDM. InvenioRDM is
* Copyright (C) 2022-2024 CERN.
*
* InvenioRDM and Knowledge Commons Works are both free software;
* you can redistribute and/or modify them under the terms of the
* MIT License; see LICENSE file for more details.
*/

import { parametrize } from "react-overridable";
import { i18next } from "@translations/i18next";
import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import { Container, Grid, Item, Table } from "semantic-ui-react";
import { InvitationsContext } from "@js/invenio_communities/api/invitations/InvitationsContextProvider";
import { RoleDropdown } from "@js/invenio_communities/members/components/dropdowns";
import RequestStatus from "@js/invenio_requests/request/RequestStatus";

const formattedTime = (expiresAt) =>
  DateTime.fromISO(expiresAt).setLocale(i18next.language).toRelative();

class InvitationResultItem extends Component {
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
    const groupName = community.custom_fields?.['kcr:commons_group_name'] || community.metadata.title;
    const memberName = member.name.replace(/knowledgeCommons---\d+\|/, `${groupName} group `);
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
                    <a href={`/collections/${community.slug}/requests/${request.id}`}>
                      {memberName}
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

const dataAttr = document.getElementById("community-invitations-search-root")?.dataset;
const community = !!dataAttr ? JSON.parse(dataAttr.community) : {};
const communitiesRolesCanInvite = !!dataAttr ? JSON.parse(dataAttr.communitiesRolesCanInvite) : {};

const InvitationResultItemWithConfig = parametrize(InvitationResultItem, {
  config: { rolesCanInvite: communitiesRolesCanInvite },
  community: community,
});

export { InvitationResultItemWithConfig, InvitationResultItem };