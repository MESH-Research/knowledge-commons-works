import { BulkActionsContext } from "./context";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { Checkbox } from "semantic-ui-react";
import _hasIn from "lodash/hasIn";

export class SearchResultsRowCheckbox extends Component {
  constructor(props) {
    super(props);
    this.state = { isChecked: false };
  }

  componentDidMount() {
    this.subscribeToContext();
    const { bulkActionContext, allSelected } = this.context;
    // eslint-disable-next-line react/no-did-mount-set-state
    this.setState({
      isChecked: this.isChecked(bulkActionContext, allSelected),
    });
  }

  static contextType = BulkActionsContext;

  isChecked = (bulkActionContext, allSelected) => {
    const { rowId } = this.props;
    if (_hasIn(bulkActionContext, `${rowId}`) || allSelected) {
      return bulkActionContext[rowId].selected;
    }
    return false;
  };

  subscribeToContext = () => {
    const { rowId, data } = this.props;
    const { allSelected, bulkActionContext } = this.context;
    if (!_hasIn(bulkActionContext, `${rowId}`)) {
      bulkActionContext[rowId] = { selected: allSelected, data: data };
    }
  };

  handleOnChange = () => {
    const { addToSelected } = this.context;
    const { rowId, data } = this.props;
    const { isChecked } = this.state;
    this.setState({ isChecked: !isChecked });
    addToSelected(rowId, data);
  };

  render() {
    const { bulkActionContext, allSelected } = this.context;
    return (
      <Checkbox
        className="mt-auto mb-auto "
        checked={this.isChecked(bulkActionContext, allSelected) || allSelected}
        onChange={this.handleOnChange}
      />
    );
  }
}

SearchResultsRowCheckbox.propTypes = {
  rowId: PropTypes.string.isRequired,
  data: PropTypes.object.isRequired,
};
