// Part of Knowledge Commons Works
// Copyright (C) 2023-2026, MESH Research
//
// Knowledge Commons Works is an instance of InvenioRDM, which is
// Copyright (c) 2019-2026, CERN
//
// Knowledge Commons Works and InvenioRDM are both free software;
// You can redistribute and/or modify them under the terms of the
// MIT License; see LICENSE file for more details.

import React from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

/**
 * Mini icon button that opens a Globus Web App URL in a new tab.
 *
 * @param {object} props
 * @param {string} props.href Globus Web App URL.
 * @param {string} [props.ariaLabel] Accessible label for the button.
 */
const GlobusExternalLinkButton = ({ href, ariaLabel }) => (
  <Button
    as="a"
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    size="mini"
    basic
    compact
    icon="external alternate"
    className="ml-5"
    aria-label={ariaLabel || i18next.t("Open in Globus")}
  />
);

export { GlobusExternalLinkButton };
