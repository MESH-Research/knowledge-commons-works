/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React from "react";

class DateFormatter extends React.Component {
  render() {
    const { value } = this.props;

    if (!value) {
      return null;
    }

    const date = DateTime.fromISO(value);
    return (
      <p data-testid="date-formatter">{date.toLocaleString(DateTime.DATETIME_MED)}</p>
    );
  }
}

DateFormatter.propTypes = {
  value: PropTypes.string.isRequired,
};

export default DateFormatter;
