/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2023 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import ReactDOM from "react-dom";

import CommunitiesCardGroup from "./CommunitiesCardGroup";

const userCommunitiesContainer = document.getElementById("user-communities");
const newCommunitiesContainer = document.getElementById("new-communities");
const topicCommunitiesContainer = document.getElementById("topic-communities");
const commonsCommunitiesContainer = document.getElementById("commons-communities");
const orgCommunitiesContainer = document.getElementById("organization-communities");
const journalCommunitiesContainer = document.getElementById("journal-communities");
const eventCommunitiesContainer = document.getElementById("event-communities");

const sections = [
  {
    container: userCommunitiesContainer,
    fetchDataUrl: "/api/user/communities?q=&sort=newest&page=1&size=5",
    emptyMessage: "You are not yet a member of any collection.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: newCommunitiesContainer,
    fetchDataUrl: "/api/communities?q=&sort=newest&page=1&size=5",
    emptyMessage: "There are no new collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: commonsCommunitiesContainer,
    fetchDataUrl: "/api/communities?q=metadata.type.id:commons&sort=newest&page=1&size=5",
    emptyMessage: "There are no commons collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: topicCommunitiesContainer,
    fetchDataUrl: "/api/communities?q=metadata.type.id:topic&sort=newest&page=1&size=5",
    emptyMessage: "There are no topic collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: orgCommunitiesContainer,
    fetchDataUrl: "/api/communities?q=metadata.type.id:organization&sort=newest&page=1&size=5",
    emptyMessage: "There are no organization collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: journalCommunitiesContainer,
    fetchDataUrl: "/api/communities?q=metadata.type.id:journal&sort=newest&page=1&size=5",
    emptyMessage: "There are no journal collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: eventCommunitiesContainer,
    fetchDataUrl: "/api/communities?q=metadata.type.id:event&sort=newest&page=1&size=5",
    emptyMessage: "There are no event collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  }
];

sections.forEach((section) => {
  if (section.container) {
    ReactDOM.render(
      <CommunitiesCardGroup
        fetchDataUrl={section.fetchDataUrl}
        emptyMessage={section.emptyMessage}
        defaultLogo={section.defaultLogo}
      />,
      section.container
    );
  }
});