/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React from "react";
import PropTypes from "prop-types";
import _get from "lodash/get";
import DateFormatter from "./DateFormatter";
import BoolFormatter from "./BoolFormatter";

const elementTypeMap = {
  datetime: DateFormatter,
  date: DateFormatter,
  bool: BoolFormatter,
};

class Formatter extends React.Component {
  render() {
    const { resourceSchema, result, property, ...uiProps } = this.props;

    const resourceSchemaProperty = property.replace(/\./g, ".properties.");
    const typePath = `${resourceSchemaProperty}.type`;

    const type = _get(resourceSchema, typePath);
    const Element = _get(elementTypeMap, type);
    const value = _get(result, property, null);
    if (Element) {
      return <Element value={value} {...uiProps} />;
    } else {
      return value;
    }
  }
}

Formatter.propTypes = {
  resourceSchema: PropTypes.object.isRequired,
  result: PropTypes.object.isRequired,
  property: PropTypes.string.isRequired,
};

export default Formatter;
