/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2023 CERN.
 * Copyright (C) 2021-2022 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import ReactDOM from "react-dom";
import { default as CommunityProfileForm } from "./CommunityProfileForm";
import { OverridableContext, overrideStore } from "react-overridable";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);
const hasLogo = JSON.parse(domContainer.dataset.hasLogo);
const types = JSON.parse(domContainer.dataset.types);
const logoMaxSize = JSON.parse(domContainer.dataset.logoMaxSize);
const customFields = JSON.parse(domContainer.dataset.customFields);
const permissions = JSON.parse(domContainer.dataset.permissions);
const overriddenComponents = overrideStore.getAll();

ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CommunityProfileForm
      community={community}
      hasLogo={hasLogo}
      defaultLogo="/static/images/square-placeholder.png"
      types={types}
      logoMaxSize={logoMaxSize}
      customFields={customFields}
      permissions={permissions}
    />
  </OverridableContext.Provider>,
  domContainer
);
