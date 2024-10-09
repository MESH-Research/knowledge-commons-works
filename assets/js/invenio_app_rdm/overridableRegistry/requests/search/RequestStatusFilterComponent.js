// This file is part of Invenio
// Copyright (C) 2023 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_requests/i18next";
import PropTypes from "prop-types";
import React, { useState, useEffect, useCallback } from "react";
import { withState } from "react-searchkit";
import { Button, Label } from "semantic-ui-react";
import { REQUEST_STATUSES } from "./types";

const RequestStatusFilterComponent = ({
  currentQueryState,
  updateQueryState,
  keepFiltersOnUpdate,
}) => {
  const [open, setOpen] = useState(undefined);

  useEffect(() => {
    const userSelectionFilters = currentQueryState.filters;
    const openFilter = userSelectionFilters.find((obj) =>
      obj.includes("is_open")
    );
    if (openFilter) {
      setOpen(openFilter.includes("true"));
    }
  }, [currentQueryState.filters]);

  const retrieveRequests = useCallback(
    (OpenStatus) => {
      if (open === OpenStatus) {
        return;
      }
      setOpen(OpenStatus);
      const newFilters = keepFiltersOnUpdate
        ? currentQueryState.filters.filter(
            (element) => element[0] !== "is_open"
          )
        : [];
      newFilters.push(["is_open", OpenStatus]);
      updateQueryState({ ...currentQueryState, filters: newFilters });
    },
    [open, currentQueryState, updateQueryState, keepFiltersOnUpdate]
  );

  const retrieveOpenRequests = useCallback(() => {
    retrieveRequests(true);
  }, [retrieveRequests]);

  const retrieveClosedRequests = useCallback(() => {
    retrieveRequests(false);
  }, [retrieveRequests]);

  const [resolvedUnreadNotifications, setResolvedUnreadNotifications] =
    useState([]);
  const [pendingUnreadNotifications, setPendingUnreadNotifications] = useState(
    []
  );

  const updateUnreadNotifications = useCallback(() => {
    const storedNotifications = sessionStorage.getItem("unreadNotifications");
    if (storedNotifications && storedNotifications !== "[]") {
      const unread = JSON.parse(storedNotifications);
      console.log("unread", unread);
      const pendingUnread = unread.filter(
        (notification) =>
          REQUEST_STATUSES.PENDING.includes(notification.request_status)
      );
      setPendingUnreadNotifications(pendingUnread);
      const resolvedUnread = unread.filter(
        (notification) =>
          REQUEST_STATUSES.RESOLVED.includes(notification.request_status)
      );
      setResolvedUnreadNotifications(resolvedUnread);
    }
  }, []);

  useEffect(() => {
    updateUnreadNotifications();
    window.addEventListener("storage", updateUnreadNotifications);

    return () => {
      window.removeEventListener("storage", updateUnreadNotifications);
    };
  }, [updateUnreadNotifications]);

  return (
    <Button.Group basic>
      <Button
        className="request-search-filter"
        onClick={retrieveOpenRequests}
        active={open === true}
      >
        {i18next.t("Pending")}

        {pendingUnreadNotifications.length > 0 && (
          <Label
            floating
            color="orange"
            className="request-search-filter-unread"
          >
            {pendingUnreadNotifications.length}
          </Label>
        )}
      </Button>
      <Button
        className="request-search-filter"
        onClick={retrieveClosedRequests}
        active={open === false}
      >
        {i18next.t("Resolved")}

        {resolvedUnreadNotifications.length > 0 && (
          <Label
            floating
            color="orange"
            className="request-search-filter-unread"
          >
            {resolvedUnreadNotifications.length}
          </Label>
        )}
      </Button>
    </Button.Group>
  );
};

RequestStatusFilterComponent.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  keepFiltersOnUpdate: PropTypes.bool,
};

RequestStatusFilterComponent.defaultProps = {
  keepFiltersOnUpdate: false,
};

export const RequestStatusFilter = withState(RequestStatusFilterComponent);
