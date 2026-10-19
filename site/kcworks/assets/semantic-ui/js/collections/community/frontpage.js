/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2023 Northwestern University.
 *
 * Modified by Mesh Research as part of Knowledge Commons Works
 * Copyright (C) 2024-2026 Mesh Research
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import ReactDOM from "react-dom";
import { OverridableContext, overrideStore } from "react-overridable";

import CommunitiesCarousel from "./communitiesCarousel/CommunitiesCarousel";

const userCommunitiesContainer = document.getElementById("user-communities");
const newCommunitiesContainer = document.getElementById("new-communities");
const topicCommunitiesContainer = document.getElementById("topic-communities");
const commonsCommunitiesContainer = document.getElementById("commons-communities");
const orgCommunitiesContainer = document.getElementById("organization-communities");
const journalCommunitiesContainer = document.getElementById("journal-communities");
const eventCommunitiesContainer = document.getElementById("event-communities");

/** Enough results to scroll past one viewport page. */
const SECTION_PAGE_SIZE = 12;
/** Visible cards per breakpoint (wired to --carousel-visible-* CSS vars). */
const SECTION_VISIBLE_DESKTOP = 5;
const SECTION_VISIBLE_TABLET = 4;
const SECTION_VISIBLE_MOBILE = 2;

const sections = [
  {
    container: userCommunitiesContainer,
    fetchUrl: `/api/user/communities?q=&sort=newest&page=1&size=${SECTION_PAGE_SIZE}`,
    emptyMessage: "You are not yet a member of any collection.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: newCommunitiesContainer,
    fetchUrl: `/api/communities?q=&sort=newest&page=1&size=${SECTION_PAGE_SIZE}`,
    emptyMessage: "There are no new collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: commonsCommunitiesContainer,
    fetchUrl: `/api/communities?q=metadata.type.id:commons&sort=newest&page=1&size=${SECTION_PAGE_SIZE}`,
    emptyMessage: "There are no commons collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: topicCommunitiesContainer,
    fetchUrl: `/api/communities?q=metadata.type.id:topic&sort=newest&page=1&size=${SECTION_PAGE_SIZE}`,
    emptyMessage: "There are no topic collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: orgCommunitiesContainer,
    fetchUrl: `/api/communities?q=metadata.type.id:organization&sort=newest&page=1&size=${SECTION_PAGE_SIZE}`,
    emptyMessage: "There are no organization collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: journalCommunitiesContainer,
    fetchUrl: `/api/communities?q=metadata.type.id:journal&sort=newest&page=1&size=${SECTION_PAGE_SIZE}`,
    emptyMessage: "There are no journal collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
  {
    container: eventCommunitiesContainer,
    fetchUrl: `/api/communities?q=metadata.type.id:event&sort=newest&page=1&size=${SECTION_PAGE_SIZE}`,
    emptyMessage: "There are no event collections.",
    defaultLogo: "/static/images/square-placeholder.png",
  },
];

const overriddenComponents = overrideStore.getAll();

sections.forEach((section) => {
  if (section.container) {
    ReactDOM.render(
      <OverridableContext.Provider value={overriddenComponents}>
        <CommunitiesCarousel
          fetchUrl={section.fetchUrl}
          defaultLogo={section.defaultLogo}
          emptyMessage={section.emptyMessage}
          itemsPerPage={SECTION_VISIBLE_DESKTOP}
          itemsPerPageTablet={SECTION_VISIBLE_TABLET}
          itemsPerPageMobile={SECTION_VISIBLE_MOBILE}
          showTitle={false}
          showMarkers={false}
          autoplay={false}
          embedded
        />
      </OverridableContext.Provider>,
      section.container
    );
  }
});
