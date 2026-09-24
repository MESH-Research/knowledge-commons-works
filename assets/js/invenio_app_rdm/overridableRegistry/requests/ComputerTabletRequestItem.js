// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  clearUnreadNotifications,
  getUnreadNotificationsFromStorage,
  UNREAD_NOTIFICATIONS_UPDATED_EVENT,
} from "@js/kcworks/notifications/unreadNotifications";
import { i18next } from "@translations/i18next";
import { default as RequestTypeIcon } from "@js/invenio_requests/components/RequestTypeIcon";
import { Trans } from "react-i18next";
import React, { useEffect, useState } from "react";
import RequestTypeLabel from "@js/invenio_requests/request/RequestTypeLabel";
import RequestStatusLabel from "@js/invenio_requests/request/RequestStatusLabel";
import { RequestActionController } from "@js/invenio_requests/request/actions/RequestActionController";
import { Button, Icon, Item, Label } from "semantic-ui-react";
import PropTypes from "prop-types";
import { toRelativeTime } from "react-invenio-forms";
import { DateTime } from "luxon";

export const ComputerTabletRequestItem = ({
  result,
  updateQueryState,
  currentQueryState,
  detailsURL,
}) => {
  const [unreadNotifications, setUnreadNotifications] = useState([]);
  const [isUnread, setIsUnread] = useState(false);
  const [isNewRequest, setIsNewRequest] = useState(false);
  const [markingRead, setMarkingRead] = useState(false);

  const createdDate = new Date(result.created);
  let creatorName = "";
  const isCreatorUser = "user" in result.created_by;
  const isCreatorCommunity = "community" in result.created_by;
  const isCreatorGuest = "email" in result.created_by;
  if (isCreatorUser) {
    creatorName =
      result.expanded?.created_by.profile?.full_name ||
      result.expanded?.created_by.username ||
      result.created_by.user;
  } else if (isCreatorCommunity) {
    creatorName =
      result.expanded?.created_by.metadata?.title || result.created_by.community;
  } else if (isCreatorGuest) {
    creatorName = result.created_by.email;
  }

  const updateUnreadNotifications = () => {
    setUnreadNotifications(getUnreadNotificationsFromStorage());
  };

  useEffect(() => {
    updateUnreadNotifications();
    window.addEventListener(
      UNREAD_NOTIFICATIONS_UPDATED_EVENT,
      updateUnreadNotifications
    );
    return () => {
      window.removeEventListener(
        UNREAD_NOTIFICATIONS_UPDATED_EVENT,
        updateUnreadNotifications
      );
    };
  }, []);

  useEffect(() => {
    const match = unreadNotifications.find(
      (notification) => notification.request_id === result.id
    );
    setIsUnread(Boolean(match));
    setIsNewRequest(match ? match.is_new_request !== false : false);
  }, [unreadNotifications, result.id]);

  const handleMarkAsRead = async (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (markingRead) {
      return;
    }
    setMarkingRead(true);
    try {
      await clearUnreadNotifications({ requestId: result.id });
    } catch (error) {
      console.error("Error marking request as read:", error);
    } finally {
      setMarkingRead(false);
    }
  };

  const getUserIcon = (receiver) => {
    return receiver?.is_ghost ? "user secret" : "users";
  };

  return (
    <Item key={result.id} className="computer tablet only flex">
      <div className="status-icon mr-10">
        <Item.Content verticalAlign="top">
          <Item.Extra>
            <RequestTypeIcon type={result.type} />
          </Item.Extra>
        </Item.Content>
      </div>
      <Item.Content>
        <Item.Extra>
          {result.type && <RequestTypeLabel type={result.type} />}
          {result.status && result.is_closed && (
            <RequestStatusLabel status={result.status} />
          )}
          {isUnread && (
            <>
              <Label color="orange" className="small horizontal">
                {isNewRequest ? i18next.t("New") : i18next.t("New comment")}
              </Label>
              <Button
                basic
                compact
                size="mini"
                className="ml-5"
                loading={markingRead}
                disabled={markingRead}
                onClick={handleMarkAsRead}
                content={i18next.t("Mark as read")}
                aria-label={i18next.t("Mark as read")}
              />
            </>
          )}
          <div className="right floated">
            <RequestActionController
              request={result}
              actionSuccessCallback={() => updateQueryState(currentQueryState)}
            />
          </div>
        </Item.Extra>
        <Item.Header className={`truncate-lines-2 ${result.is_closed && "mt-5"}`}>
          <a className="header-link" href={detailsURL}>
            {result.title}
          </a>
        </Item.Header>
        <Item.Meta>
          <small>
            {i18next.t("Opened {{relativeTime}} by", {
              relativeTime: toRelativeTime(createdDate.toISOString(), i18next.language)
            })}
            {" "}
            {creatorName}
          </small>
          <small className="right floated">
            {result.receiver.community && result.expanded?.receiver.metadata.title && (
              <>
                <Icon
                  className="default-margin"
                  name={getUserIcon(result.expanded?.receiver)}
                />
                <span className="ml-5">{result.expanded?.receiver.metadata.title}</span>
              </>
            )}
            {result.expires_at && (
              <span>
                {i18next.t("Expires at: {{- expiringDate}}", {
                  expiringDate: DateTime.fromISO(result.expires_at).toLocaleString(
                    i18next.language
                  ),
                })}
              </span>
            )}
          </small>
        </Item.Meta>
      </Item.Content>
    </Item>
  );
};

ComputerTabletRequestItem.propTypes = {
  result: PropTypes.object.isRequired,
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  detailsURL: PropTypes.string.isRequired,
};
