// This file is part of InvenioAdministration
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component } from "react";
import Overridable from "react-overridable";
import { Table } from "semantic-ui-react";
import Formatter from "../components/Formatter";

class DetailsTable extends Component {
  render() {
    const { schema, data, uiSchema } = this.props;
    let fields = uiSchema ? uiSchema : schema;

    const tableRows = Object.entries(fields).map(([field, fieldSchema]) => {
      const text = fieldSchema.text || field;

      return (
        <Table.Row key={text}>
          <Table.Cell width={3}>
            <b>{text}</b>
          </Table.Cell>
          <Table.Cell>
            {" "}
            <Formatter result={data} resourceSchema={schema} property={field} />
          </Table.Cell>
        </Table.Row>
      );
    });

    return (
      <Overridable id="DetailsComponent.table">
        <Table unstackable>
          <Table.Body>{tableRows}</Table.Body>
        </Table>
      </Overridable>
    );
  }
}

DetailsTable.propTypes = {
  data: PropTypes.object.isRequired,
  schema: PropTypes.object.isRequired,
  uiSchema: PropTypes.object.isRequired,
};

export default Overridable.component("DetailsTable", DetailsTable);
