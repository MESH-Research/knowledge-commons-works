/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import PropTypes from "prop-types";
import React from "react";
import { Table } from "semantic-ui-react";
import isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/invenio_administration/i18next";

export const SearchResultsContainer = ({
  results,
  columns,
  displayEdit,
  displayDelete,
  actions,
}) => {
  const resourceHasActions = displayEdit || displayDelete || !isEmpty(actions);

  return (
    <Table>
      <Table.Header>
        <Table.Row>
          {columns.map(([property, { text, order, width }], index) => {
            if (!width) {
              width = index === 0 ? undefined : index === 1 ? 4 : 3;
            }

            return (
              <Table.HeaderCell key={property + order} width={width}>
                {text}
              </Table.HeaderCell>
            );
          })}
          {resourceHasActions && (
            <Table.HeaderCell collapsing>{i18next.t("Actions")}</Table.HeaderCell>
          )}
        </Table.Row>
      </Table.Header>
      <Table.Body>{results}</Table.Body>
    </Table>
  );
};

SearchResultsContainer.propTypes = {
  results: PropTypes.array.isRequired,
  columns: PropTypes.array.isRequired,
  displayEdit: PropTypes.bool,
  displayDelete: PropTypes.bool,
  actions: PropTypes.object.isRequired,
};

SearchResultsContainer.defaultProps = {
  displayDelete: true,
  displayEdit: true,
};
