/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createSearchAppInit } from "@js/invenio_search_ui";
import { NotificationController } from "../ui_messages/context";
import { initDefaultSearchComponents } from "./SearchComponents";

const domContainer = document.getElementById("invenio-search-config");

const defaultComponents = initDefaultSearchComponents(domContainer);

createSearchAppInit(
  defaultComponents,
  true,
  "invenio-search-config",
  false,
  NotificationController
);
