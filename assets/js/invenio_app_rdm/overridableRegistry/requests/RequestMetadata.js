// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_requests/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Divider, Header, Icon, Message } from "semantic-ui-react";
import { toRelativeTime } from "react-invenio-forms";
import RequestStatus from "./RequestStatus";
import RequestTypeLabel from "./RequestTypeLabel";

const User = ({ user }) => (
  <div className="flex">
    <Image
      src={user.links.avatar}
      avatar
      size="tiny"
      className="mr-5"
      ui={false}
      rounded
    />
    <span>
      {user.profile?.full_name ||
        user?.username ||
        user?.email ||
        i18next.t("Anonymous user")}
    </span>
  </div>
);
const Community = ({ community }) => (
  <div className="flex">
    <Image src={community.links.logo} avatar size="tiny" className="mr-5" ui={false} />
    <a href={`/collections/${community.slug}`}>{community.metadata.title}</a>
  </div>
);
const ExternalEmail = ({ email }) => (
  <div className="flex">
    <Icon name="mail" className="mr-5" />
    <span>
      {i18next.t("Email")}: {email.id}
    </span>
  </div>
);
const Group = ({ group }) => (
  <div className="flex">
    <Icon name="group" className="mr-5" />
    <span>
      {i18next.t("Group")}: {group?.name}
    </span>
  </div>
);

const EntityDetails = ({ userData, details }) => {
  const isUser = "user" in userData;
  const isCommunity = "community" in userData;
  const isExternalEmail = "email" in userData;
  const isGroup = "group" in userData;

  if (isUser) {
    return <User user={details} />;
  } else if (isCommunity) {
    return <Community community={details} />;
  } else if (isExternalEmail) {
    return <ExternalEmail email={details} />;
  } else if (isGroup) {
    return <Group group={details} />;
  }
  return null;
};

const DeletedResource = ({ details }) => (
  <Message negative>{details.metadata.title}</Message>
);

class RequestMetadata extends Component {
  isResourceDeleted = (details) => details.is_ghost === true;

  render() {
    const { request } = this.props;
    const expandedCreatedBy = request.expanded?.created_by;
    const expandedReceiver = request.expanded?.receiver;
    return (
      <Overridable id="InvenioRequest.RequestMetadata.Layout" request={request}>
        <>
          {expandedCreatedBy !== undefined && (
            <>
              <Header as="h3" size="tiny">
                {i18next.t("Creator")}
              </Header>
              {this.isResourceDeleted(expandedCreatedBy) ? (
                <DeletedResource details={expandedCreatedBy} />
              ) : (
                <EntityDetails
                  userData={request.created_by}
                  details={request.expanded?.created_by}
                />
              )}
              <Divider />
            </>
          )}

          <Header as="h3" size="tiny">
            {i18next.t("Receiver")}
          </Header>
          {this.isResourceDeleted(expandedReceiver) ? (
            <DeletedResource details={expandedReceiver} />
          ) : (
            <EntityDetails
              userData={request.receiver}
              details={request.expanded?.receiver}
            />
          )}
          <Divider />

          <Header as="h3" size="tiny">
            {i18next.t("Request type")}
          </Header>
          <RequestTypeLabel type={request.type} />
          <Divider />

          <Header as="h3" size="tiny">
            {i18next.t("Status")}
          </Header>
          <RequestStatus status={request.status} />
          <Divider />

          <Header as="h3" size="tiny">
            {i18next.t("Created")}
          </Header>
          {toRelativeTime(request.created, i18next.language)}

          {request.expires_at && (
            <>
              <Divider />
              <Header as="h3" size="tiny">
                {i18next.t("Expires")}
              </Header>
              {toRelativeTime(request.expires_at, i18next.language)}
            </>
          )}

          {request.status === "accepted" && request.topic?.record && (
            <>
              <Divider />
              <Header as="h3" size="tiny">
                {i18next.t("Record")}
              </Header>
              <a href={`/records/${request.topic.record}`}>{request.title}</a>
            </>
          )}
        </>
      </Overridable>
    );
  }
}

RequestMetadata.propTypes = {
  request: PropTypes.object.isRequired,
};

export default Overridable.component(
  "InvenioRequests.RequestMetadata",
  RequestMetadata
);
