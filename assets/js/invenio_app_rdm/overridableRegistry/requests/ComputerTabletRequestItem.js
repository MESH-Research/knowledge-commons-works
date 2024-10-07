// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_requests/i18next";
import { default as RequestTypeIcon } from "@js/invenio_requests/components/RequestTypeIcon";
import { Trans } from "react-i18next";
import React, { useEffect, useState } from "react";
import RequestTypeLabel from "@js/invenio_requests/request/RequestTypeLabel";
import RequestStatusLabel from "@js/invenio_requests/request/RequestStatusLabel";
import { RequestActionController } from "@js/invenio_requests/request/actions/RequestActionController";
import { Icon, Item, Label } from "semantic-ui-react";
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
  const [hasUnreadComments, setHasUnreadComments] = useState(false);

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
    const storedNotifications = sessionStorage.getItem('unreadNotifications');
    if (storedNotifications) {
      setUnreadNotifications(JSON.parse(storedNotifications));
    }
  }

  useEffect(() => {
    updateUnreadNotifications();
    window.addEventListener("storage", updateUnreadNotifications);
    return () => {
      window.removeEventListener("storage", updateUnreadNotifications);
    }
  }, []);

  useEffect(() => {
    const isUnread = unreadNotifications.some(notification => notification.request_id === result.id);
    const hasUnreadComments = unreadNotifications.some(notification => notification.request_id === result.id && notification.unread_comments?.length > 0);
    setIsUnread(isUnread);
    setHasUnreadComments(hasUnreadComments);
  }, [unreadNotifications, result.id]);

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
            <Label color="orange" className="small horizontal">{ hasUnreadComments ? i18next.t("New") : i18next.t("New comment") }</Label>
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
            <Trans
              defaults="Opened {{relativeTime}} by"
              values={{
                relativeTime: toRelativeTime(
                  createdDate.toISOString(),
                  i18next.language
                ),
              }}
            />{" "}
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
