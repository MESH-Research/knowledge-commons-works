/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { RequestActionContext } from "@js/invenio_requests";

export class ActionButtons extends Component {
  static contextType = RequestActionContext;

  render() {
    const { linkExtractor } = this.context;
    return (
      <Button
        as="a"
        target="_blank"
        size="medium"
        content={i18next.t("View")}
        href={linkExtractor.self_html}
      />
    );
  }
}

ActionButtons.propTypes = {};
