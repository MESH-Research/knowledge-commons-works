/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import PropTypes from "prop-types";
import React from "react";
import { Icon } from "semantic-ui-react";
import Overridable from "react-overridable";

class BoolFormatter extends React.Component {
  render() {
    const { value, icon, color } = this.props;
    if (!value) {
      return null;
    }
    return <Icon name={icon} color={color} />;
  }
}

BoolFormatter.propTypes = {
  value: PropTypes.string.isRequired,
  icon: PropTypes.string,
  color: PropTypes.string,
};

BoolFormatter.defaultProps = {
  icon: "check",
  color: "green",
};

export default Overridable.component(
  "InvenioAdministration.BoolFormatter",
  BoolFormatter
);
