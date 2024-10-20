// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import axios from "axios";
import { i18next } from "@translations/invenio_requests/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import GeoPattern from "geopattern";
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
const Community = ({ community, pattern }) => (
  <div className="flex">
    <Image src={community.links.logo} avatar size="tiny" className="mr-5" ui={false} fallbackSrc={pattern.toDataUri()} />
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
    const pattern = GeoPattern.generate(encodeURI(details.slug));
    return <Community community={details} pattern={pattern} />;
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

const RequestMetadata = ({ request }) => {
  const isResourceDeleted = (details) => details.is_ghost === true;

  const expandedCreatedBy = request.expanded?.created_by;
  const expandedReceiver = request.expanded?.receiver;

  // Get unread notifications from session storage
  const unreadNotifications = JSON.parse(sessionStorage.getItem('unreadNotifications')) || [];

  // Check if the current request.id is in unreadNotifications
  const isUnread = unreadNotifications.some(notification => notification.request_id === request.id);

  // Determine if the request should clear the unread notification
  // - For submissions and inclusions, the creator should clear their own unread
  //   request notifications.
  // - For invitations, the receiver should clear their own unread request
  //   notifications.
  // - Otherwise, the request should not clear the unread notification by
  //   default.
  //
  // Returns the user's id if the request should clear the unread notification,
  // false otherwise.
  const shouldClear = (request) => {
    let creator_reading = null;
    if (request.expanded?.created_by?.is_current_user === true) {
      creator_reading = request.expanded.created_by.id;
    }
    let receiver_reading = null;
    if (request.expanded?.receiver?.is_current_user === true) {
      receiver_reading = request.expanded.receiver.id;
    }

    if (request.type === "community-submission" || request.type === "community-inclusion") {
      if (!!isUnread && !!creator_reading) {
        return creator_reading;
      }
    } else if (request.type === "community-invitation") {
      if (!!isUnread && !!receiver_reading) {
        return receiver_reading;
      }
    }
    return false;
  }

  const userToClear = shouldClear(request);

  if (!!userToClear) {

    const apiConfig = {
      withCredentials: true,
      xsrfCookieName: "csrftoken",
      xsrfHeaderName: "X-CSRFToken",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/vnd.inveniordm.v1+json",
      },
    };
    const axiosWithConfig = axios.create(apiConfig);

    axiosWithConfig.get(`/api/users/${userToClear}/notifications/unread/clear`, {
      params: {request_id: request.id},
    })
    .then(response => {
      // Update the unreadNotifications in session storage
      sessionStorage.setItem('unreadNotifications', JSON.stringify(response.data));
      // Dispatch a storage event to update other components that are listening
      window.dispatchEvent(new Event("storage"));
    })
    .catch(error => {
      console.error('Error clearing unread notification:', error);
    });
  }

  return (
      <>
        {expandedCreatedBy !== undefined && (
          <>
            <Header as="h3" size="tiny">
              {i18next.t("Creator")}
            </Header>
            {isResourceDeleted(expandedCreatedBy) ? (
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
        {isResourceDeleted(expandedReceiver) ? (
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
  );
}

RequestMetadata.propTypes = {
  request: PropTypes.object.isRequired,
};

export { RequestMetadata };
