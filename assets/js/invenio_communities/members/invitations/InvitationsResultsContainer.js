/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Table } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";

export const InvitationsResultsContainer = ({ results }) => {
  return (
    <Table>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell width={6}>{i18next.t("Name")}</Table.HeaderCell>
          <Table.HeaderCell width={2}>{i18next.t("Status")}</Table.HeaderCell>
          <Table.HeaderCell width={2}>{i18next.t("Expires")}</Table.HeaderCell>
          <Table.HeaderCell width={4}>{i18next.t("Role")}</Table.HeaderCell>
          <Table.HeaderCell width={2} />
        </Table.Row>
      </Table.Header>
      <Table.Body>{results}</Table.Body>
    </Table>
  );
};

InvitationsResultsContainer.propTypes = {
  results: PropTypes.array.isRequired,
};
