// This file is part of InvenioAdministration
// Copyright (C) 2022 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import { EditPage } from "./EditPage";
import _get from "lodash/get";
import { NotificationController } from "../ui_messages/context";

const domContainer = document.getElementById("invenio-administration-edit-root");
const resourceSchema = JSON.parse(domContainer.dataset.resourceSchema);
const apiEndpoint = _get(domContainer.dataset, "apiEndpoint");
const pid = JSON.parse(domContainer.dataset.pid);
const formFields = JSON.parse(domContainer.dataset.formFields);
const listUIEndpoint = domContainer.dataset.listEndpoint;

ReactDOM.render(
  <NotificationController>
    <EditPage
      resourceSchema={resourceSchema}
      apiEndpoint={apiEndpoint}
      formFields={formFields}
      pid={pid}
      listUIEndpoint={listUIEndpoint}
    />
  </NotificationController>,
  domContainer
);
