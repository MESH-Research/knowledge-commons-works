/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React from "react";
import ReactDOM from "react-dom";
import FeaturedCommunities from "./FeaturedCommunities";

const featuredCommunitiesContainer = document.getElementById("communities-featured");
const columnNumber = featuredCommunitiesContainer.dataset.columnNumber;
const mobileColumnWidth = featuredCommunitiesContainer.dataset.mobileColumnWidth;
const tabletColumnWidth = featuredCommunitiesContainer.dataset.tabletColumnWidth;
const computerColumnWidth = featuredCommunitiesContainer.dataset.computerColumnWidth;
const widescreenColumnWidth =
  featuredCommunitiesContainer.dataset.widescreenColumnWidth;

ReactDOM.render(
  <FeaturedCommunities
    columnNumber={columnNumber}
    mobileColumnWidth={mobileColumnWidth}
    computerColumnWidth={computerColumnWidth}
    tabletColumnWidth={tabletColumnWidth}
    widescreenColumnWidth={widescreenColumnWidth}
  />,
  featuredCommunitiesContainer
);
