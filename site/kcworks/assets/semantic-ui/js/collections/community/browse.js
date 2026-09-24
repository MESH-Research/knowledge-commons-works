/*
 * Based on a file in Invenio App RDM
 * Copyright (C) 2024 CERN.
 *
 * Modifications for Knowledge Commons Works
 * Copyright (C) 2026 Mesh Research
 *
 * Invenio and Knowledge Commons Works are both free software; you
 * can redistribute and/or modify them under the terms of the MIT License;
 * see LICENSE file for more details.
 */

import React from "react";
import ReactDOM from "react-dom";
import _get from "lodash/get";
import { i18next } from "@translations/kcworks/i18next";

import CommunitiesCardGroup from "./CommunitiesCardGroup";

const subCommunitiesContainer = document.getElementById("subcommunities-container");
const apiEndpoint = subCommunitiesContainer
  ? _get(subCommunitiesContainer.dataset, "apiEndpoint")
  : undefined;

if (subCommunitiesContainer && apiEndpoint) {
  ReactDOM.render(
    <CommunitiesCardGroup
      fetchDataUrl={`${apiEndpoint}?sort=oldest&page=1&size=5`}
      emptyMessage={i18next.t("This community has no subcommunities")}
      defaultLogo="/static/images/square-placeholder.png"
    />,
    subCommunitiesContainer
  );
}
