// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_requests/i18next";
import React from "react";
import TimelineActionEvent from "../components/TimelineActionEvent";

export const TimelineAcceptEvent = ({ event }) => (
  <TimelineActionEvent
    iconName="check circle"
    iconColor="positive"
    event={event}
    eventContent={i18next.t("accepted this request")}
  />
);

export const TimelineDeclineEvent = ({ event }) => (
  <TimelineActionEvent
    iconName="close"
    event={event}
    eventContent={i18next.t("declined this request")}
    iconColor="negative"
  />
);

export const TimelineExpireEvent = ({ event }) => (
  <TimelineActionEvent
    iconName="calendar times"
    event={event}
    eventContent={i18next.t("this request expired")}
    iconColor="negative"
  />
);

export const TimelineCancelEvent = ({ event }) => (
  <TimelineActionEvent
    iconName="close"
    event={event}
    eventContent={i18next.t("cancelled this request")}
    iconColor="negative"
  />
);

export const TimelineUnknownEvent = ({ event }) => (
  <TimelineActionEvent
    iconName="close"
    iconColor="negative"
    event={event}
    eventContent={i18next.t("unknown event")}
  />
);

export const TimelineCommentDeletionEvent = ({ event }) => (
  <TimelineActionEvent
    iconName="erase"
    iconColor="grey"
    event={event}
    eventContent={i18next.t("deleted a comment")}
  />
);
