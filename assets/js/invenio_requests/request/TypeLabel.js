// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { Label } from "semantic-ui-react";
import { i18next } from "@translations/invenio_requests/i18next";

export const LabelTypeSubmission = (props) => (
  <Label {...props}>{i18next.t("New submission")}</Label>
);

export const LabelTypeInvitation = (props) => (
  <Label {...props}>{i18next.t("New invitation")}</Label>
);
