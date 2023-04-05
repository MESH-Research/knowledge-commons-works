// This file is part of InvenioCommunities
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { FeatureModal } from "./FeatureModal";
import React from "react";
import ReactDOM from "react-dom";
import _get from "lodash/get";
import { OverridableContext, parametrize } from "react-overridable";
import { FeaturedEntries } from "./featured";
import { AdminDetailsView, Edit, Delete } from "@js/invenio_administration";
import { i18next } from "@translations/invenio_communities/i18next";

const domContainer = document.getElementById("invenio-details-config");
const title = domContainer.dataset.title;
const fields = JSON.parse(domContainer.dataset.fields);
const pidValue = JSON.parse(domContainer.dataset.pid);
const resourceName = JSON.parse(domContainer.dataset.resourceName);
const displayEdit = JSON.parse(domContainer.dataset.displayEdit);
const displayDelete = JSON.parse(domContainer.dataset.displayDelete);
const actions = JSON.parse(domContainer.dataset.actions);
const apiEndpoint = _get(domContainer.dataset, "apiEndpoint");
const idKeyPath = JSON.parse(_get(domContainer.dataset, "pidPath", "pid"));
const listUIEndpoint = domContainer.dataset.listEndpoint;
const resourceSchema = JSON.parse(domContainer.dataset.resourceSchema);
const uiSchema = JSON.parse(domContainer.dataset?.uiConfig);
const requestHeaders = JSON.parse(domContainer.dataset?.requestHeaders);

const createdBySystem = (data) => data?.system_created;

const overridenComponents = {
  "InvenioAdministration.EditAction": parametrize(Edit, {
    disable: createdBySystem,
    disabledMessage: i18next.t(
      "This set is not editable as it was created by the system."
    ),
  }),
  "InvenioAdministration.DeleteAction": parametrize(Delete, {
    disable: createdBySystem,
    disabledMessage: i18next.t(
      "This set is not deletable as it was created by the system."
    ),
  }),
  "InvenioAdministration.ActionModal.layout": FeatureModal,
};

domContainer &&
  ReactDOM.render(
    <OverridableContext.Provider value={overridenComponents}>
      <AdminDetailsView
        title={title}
        actions={actions}
        apiEndpoint={apiEndpoint}
        columns={fields}
        displayEdit={displayEdit}
        displayDelete={displayDelete}
        pid={pidValue}
        idKeyPath={idKeyPath}
        resourceName={resourceName}
        listUIEndpoint={listUIEndpoint}
        resourceSchema={resourceSchema}
        requestHeaders={requestHeaders}
        uiSchema={uiSchema}
      >
        <FeaturedEntries />
      </AdminDetailsView>
    </OverridableContext.Provider>,
    domContainer
  );
