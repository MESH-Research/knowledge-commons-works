// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Feed } from "semantic-ui-react";
import { timestampToRelativeTime } from "../utils";
import RequestsFeed from "./RequestsFeed";
import { TimelineEventBody } from "./TimelineEventBody";

class TimelineActionEvent extends Component {
  render() {
    const { event, iconName, iconColor, eventContent } = this.props;

    const createdBy = event.created_by;
    const isUser = "user" in createdBy;
    const expandedCreatedBy = event.expanded?.created_by;

    let userAvatar,
      user = null;
    if (isUser) {
      userAvatar = <Image
                      src={expandedCreatedBy.links.avatar}
                      avatar
                      size="tiny"
                      className="mr-5"
                      ui={false}
                    />;
      user = expandedCreatedBy.profile?.full_name || expandedCreatedBy.username;
    }

    return (
      <Overridable
        id="TimelineActionEvent.layout"
        event={event}
        iconName={iconName}
        iconColor={iconColor}
      >
        <RequestsFeed.Item>
          <RequestsFeed.Content isEvent={true}>
            <RequestsFeed.Icon name={iconName} size="large" color={iconColor} />
            <RequestsFeed.Event isActionEvent={true}>
              <Feed.Content>
                <Feed.Summary className="flex">
                  {userAvatar}
                  <b>{user}</b>
                  <Feed.Date>
                    <TimelineEventBody
                      content={eventContent}
                      format={event?.payload?.format}
                    />
                    {" "}{timestampToRelativeTime(event.created)}
                  </Feed.Date>
                </Feed.Summary>
              </Feed.Content>
            </RequestsFeed.Event>
          </RequestsFeed.Content>
        </RequestsFeed.Item>
      </Overridable>
    );
  }
}

TimelineActionEvent.propTypes = {
  event: PropTypes.object.isRequired,
  iconName: PropTypes.string.isRequired,
  eventContent: PropTypes.string.isRequired,
  iconColor: PropTypes.string,
};

TimelineActionEvent.defaultProps = {
  iconColor: "grey",
};

export default Overridable.component(
  "TimelineActionEvent",
  TimelineActionEvent
);
