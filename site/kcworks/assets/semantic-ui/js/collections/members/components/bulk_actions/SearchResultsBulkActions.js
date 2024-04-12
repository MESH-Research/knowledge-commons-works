/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_communities/i18next";
import { Checkbox, Dropdown } from "semantic-ui-react";
import { BulkActionsContext } from "./context";
import Overridable from "react-overridable";
import _pickBy from "lodash/pickBy";

export class SearchResultsBulkActions extends Component {
  constructor(props) {
    super(props);
    const { allSelected } = this.props;
    this.state = { allSelectedChecked: allSelected };
  }

  componentDidMount() {
    const { allSelected } = this.context;
    // eslint-disable-next-line react/no-did-mount-set-state
    this.setState({ allSelectedChecked: allSelected });
  }

  static contextType = BulkActionsContext;

  handleOnChange = () => {
    const { setAllSelected, allSelected } = this.context;
    this.setState({ allSelectedChecked: !allSelected });
    setAllSelected(!allSelected, true);
  };

  handleActionOnChange = (e, { value, ...props }) => {
    if (!value) return;

    const { optionSelectionCallback } = this.props;

    const { selectedCount, bulkActionContext } = this.context;
    const selected = _pickBy(bulkActionContext, ({ selected }) => selected === true);
    optionSelectionCallback(value, selected, selectedCount);
  };

  render() {
    const { bulkDropdownOptions } = this.props;
    const { allSelectedChecked } = this.state;
    const { allSelected, selectedCount } = this.context;

    const noneSelected = selectedCount === 0;

    const dropdownOptions = bulkDropdownOptions.map(({ key, value, text }) => ({
      key: key,
      value: value,
      text: text,
      disabled: noneSelected,
    }));

    return (
      <Overridable id="InvenioCommunities.SearchResultsBulkActionsManager.layout">
        <div className="flex">
          <Checkbox
            className="align-self-center mr-10"
            onChange={this.handleOnChange}
            checked={allSelectedChecked && allSelected}
            aria-label={i18next.t("Select all members")}
          />
          <Dropdown
            className="align-self-center fluid-responsive"
            text={i18next.t("{{count}} members selected", {
              count: selectedCount,
            })}
            options={dropdownOptions}
            aria-label={i18next.t("bulk actions")}
            item
            selection
            value={null}
            selectOnBlur={false}
            onChange={this.handleActionOnChange}
            selectOnNavigation={false}
          />
        </div>
      </Overridable>
    );
  }
}

SearchResultsBulkActions.propTypes = {
  bulkDropdownOptions: PropTypes.array.isRequired,
  allSelected: PropTypes.bool,
  optionSelectionCallback: PropTypes.func.isRequired,
};

SearchResultsBulkActions.defaultProps = {
  allSelected: false,
};

export default Overridable.component(
  "SearchResultsBulkActions",
  SearchResultsBulkActions
);
