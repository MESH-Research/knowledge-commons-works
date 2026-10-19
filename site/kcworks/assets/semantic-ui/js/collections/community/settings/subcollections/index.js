/*
 * This file is part of Knowledge Commons Works.
 * Copyright (C) 2026 Mesh Research.
 */

import React from "react";
import ReactDOM from "react-dom";
import CommunitySubcollectionsForm from "./CommunitySubcollectionsForm";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);

ReactDOM.render(
  <CommunitySubcollectionsForm community={community} />,
  domContainer
);
