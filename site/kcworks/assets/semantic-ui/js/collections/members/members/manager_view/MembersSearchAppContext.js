import { MembersContextProvider } from "../../../api/members/MembersContextProvider";
import SearchResultsBulkActionsManager from "../../../members/components/bulk_actions/SearchResultsBulkActionsManager";
import PropTypes from "prop-types";
import React, { Component } from "react";

export class MembersSearchAppContext extends Component {
  render() {
    const { children, community } = this.props;
    return (
      <SearchResultsBulkActionsManager>
        <MembersContextProvider community={community}>
          {children}
        </MembersContextProvider>
      </SearchResultsBulkActionsManager>
    );
  }
}

MembersSearchAppContext.propTypes = {
  community: PropTypes.object.isRequired,
  children: PropTypes.node.isRequired,
};
