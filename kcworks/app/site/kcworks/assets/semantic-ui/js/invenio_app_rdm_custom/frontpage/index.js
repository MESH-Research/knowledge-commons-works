// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import { RecordsListOverridable } from "@js/invenio_app_rdm/frontpage/RecordsList";
import { OverridableContext, overrideStore } from "react-overridable";
import { set } from "lodash";

const recordsListContainer = document.getElementById("records-list");
const title = recordsListContainer.dataset.title;
const fetchUrl = recordsListContainer.dataset.fetchUrl;
// FIXME: Changed the appName to "InvenioAppRdm.RecordsList" to match the usual
// appName in the mapping.js file for invenio_app_rdm components.
const appName = "InvenioAppRdm.RecordsList";

// FIXME: Add the overridden components directly from the override store to
// the context provider. When this is set with a variable calling
// overrideStore.getAll(), it sets value to an empty object.
ReactDOM.render(
  <OverridableContext.Provider value={overrideStore.components}>
    <RecordsListOverridable title={title} fetchUrl={fetchUrl} appName={appName} />
  </OverridableContext.Provider>,
  recordsListContainer
);
