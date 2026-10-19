/*
 * This file is part of Knowledge Commons Works.
 *   Copyright (C) 2024-2026 Mesh Research.
 *
 * Based on Invenio Requests RequestsResults.
 *   Copyright (C) 2023 CERN.
 *
 * InvenioRDM and Knowledge Commons Works are both free software;
 * you can redistribute and/or modify them under the terms of the
 * MIT License; see LICENSE file for more details.
 */

import {
  clearUnreadNotifications,
  getUnreadNotificationsFromStorage,
  UNREAD_NOTIFICATIONS_UPDATED_EVENT,
} from "@js/kcworks/notifications/unreadNotifications";
import { InvenioSearchPagination } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_requests/i18next";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { Count, ResultsList, Sort } from "react-searchkit";
import { Button, Grid, Segment } from "semantic-ui-react";

/**
 * Dashboard requests results pane with mark-all-as-read beside the count.
 *
 * @param {object} props Component props from SearchApp results pane.
 * @returns {JSX.Element|null} Results segment, or null when total is empty.
 */
export const RequestsResults = ({
  sortOptions,
  paginationOptions,
  currentResultsState,
}) => {
  const { total } = currentResultsState.data;
  const [unreadCount, setUnreadCount] = useState(
    () => getUnreadNotificationsFromStorage().length
  );
  const [markingAllRead, setMarkingAllRead] = useState(false);

  const syncUnreadCount = () => {
    setUnreadCount(getUnreadNotificationsFromStorage().length);
  };

  useEffect(() => {
    syncUnreadCount();
    window.addEventListener(UNREAD_NOTIFICATIONS_UPDATED_EVENT, syncUnreadCount);
    return () => {
      window.removeEventListener(
        UNREAD_NOTIFICATIONS_UPDATED_EVENT,
        syncUnreadCount
      );
    };
  }, []);

  const handleMarkAllAsRead = async () => {
    if (markingAllRead || unreadCount === 0) {
      return;
    }
    setMarkingAllRead(true);
    try {
      await clearUnreadNotifications();
    } catch (error) {
      console.error("Error marking all notifications as read:", error);
    } finally {
      setMarkingAllRead(false);
    }
  };

  const handleResultsRendered = () => {
    window.invenio?.onSearchResultsRendered();
  };

  return (
    total && (
      <Grid>
        <Grid.Row>
          <Grid.Column width={16}>
            <Segment>
              <Grid>
                <Grid.Row
                  verticalAlign="middle"
                  className="small pt-5 pb-5 highlight-background"
                >
                  <Grid.Column width={8} verticalAlign="middle">
                    <Count
                      label={() => (
                        <>
                          {i18next.t("{{count}} results found", {
                            count: total,
                          })}
                        </>
                      )}
                    />
                    {unreadCount > 0 && (
                      <Button
                        basic
                        compact
                        size="mini"
                        className="ml-10"
                        loading={markingAllRead}
                        disabled={markingAllRead}
                        onClick={handleMarkAllAsRead}
                        content={i18next.t("Mark all as read")}
                        aria-label={i18next.t("Mark all as read")}
                      />
                    )}
                  </Grid.Column>
                  <Grid.Column width={8} textAlign="right">
                    {sortOptions && (
                      <Sort
                        values={sortOptions}
                        label={(cmp) => (
                          <>
                            <label className="mr-10">
                              {i18next.t("Sort by")}
                            </label>
                            {cmp}
                          </>
                        )}
                      />
                    )}
                  </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                  <Grid.Column>
                    <ResultsList onResultsRendered={handleResultsRendered} />
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Segment>
          </Grid.Column>
        </Grid.Row>
        <InvenioSearchPagination paginationOptions={paginationOptions} />
      </Grid>
    )
  );
};

RequestsResults.propTypes = {
  sortOptions: PropTypes.object.isRequired,
  paginationOptions: PropTypes.object.isRequired,
  currentResultsState: PropTypes.object.isRequired,
};
