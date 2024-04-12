import { CommunityMembersApi } from "../../api/members/api";
import React, { Component } from "react";
import PropTypes from "prop-types";

export const MembersContext = React.createContext({ api: undefined });

export class MembersContextProvider extends Component {
  constructor(props) {
    super(props);
    const { community } = props;
    this.apiClient = new CommunityMembersApi(community);
  }

  render() {
    const { children } = this.props;
    return (
      <MembersContext.Provider value={{ api: this.apiClient }}>
        {children}
      </MembersContext.Provider>
    );
  }
}

MembersContextProvider.propTypes = {
  community: PropTypes.object.isRequired,
  children: PropTypes.node.isRequired,
};
