import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Header, Icon, Segment, Grid } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { i18next } from "@translations/invenio_communities/i18next";
import { InvitationsContextProvider } from "../../api/invitations/InvitationsContextProvider";
import { InvitationsMembersModalWithSearchKit } from "./invitationsModal/InvitationsMembersModal";

class InvitationsEmptyResultsCmp extends Component {
  render() {
    const {
      resetQuery,
      extraContent,
      queryString,
      community,
      communityGroupsEnabled,
      rolesCanInvite,
    } = this.props;

    return (
      <Segment.Group>
        <Segment as={Grid} className="computer only">
          <Grid.Column width="13" />
          <Grid.Column width="3">
            <InvitationsContextProvider community={community}>
              <InvitationsMembersModalWithSearchKit
                rolesCanInvite={rolesCanInvite}
                groupsEnabled={communityGroupsEnabled}
                community={community}
              />
            </InvitationsContextProvider>
          </Grid.Column>
        </Segment>
        <Segment placeholder textAlign="center">
          <Header icon>
            <Icon name="search" />
            {i18next.t("No matching members found.")}
          </Header>
          {queryString && (
            <p>
              <em>
                {i18next.t("Current search")} "{queryString}"
              </em>
            </p>
          )}
          <Button primary onClick={() => resetQuery()}>
            {i18next.t("Clear query")}
          </Button>
          {extraContent}
        </Segment>
      </Segment.Group>
    );
  }
}

InvitationsEmptyResultsCmp.propTypes = {
  resetQuery: PropTypes.func.isRequired,
  queryString: PropTypes.string.isRequired,
  rolesCanInvite: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  communityGroupsEnabled: PropTypes.bool.isRequired,
  extraContent: PropTypes.node,
};

InvitationsEmptyResultsCmp.defaultProps = {
  extraContent: null,
};

export const InvitationsEmptyResults = withState(InvitationsEmptyResultsCmp);
