/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image, withCancel } from "react-invenio-forms";
import { Dropdown, List } from "semantic-ui-react";
import _truncate from "lodash/truncate";

export class MembersSearchBar extends Component {
  constructor(props) {
    super(props);

    this.state = {
      isFetching: false,
      error: false,
      suggestions: [],
    };
  }

  serializeMemberName = (person) => {
    const name = person.profile?.full_name;

    const displayName = name
      ? `${name} <${person.email || person.username}>`
      : person.email
      ? `${person.email} <${person.username}>`
      : `<${person.username}>`;

    return displayName;
  };

  serializeUsersForDropdown = (users) => {
    return users.map((person) => {
      return {
        text: person.id,
        value: person.id,
        key: person.id,
        content: (
          <List divided relaxed key={person.id}>
            <List.Item key={person.id}>
              <Image size="mini" src={person.links.avatar} avatar />
              <List.Content>
                <List.Header as="a">{this.serializeMemberName(person)}</List.Header>
                <List.Description>{person.profile.affiliations}</List.Description>
              </List.Content>
            </List.Item>
          </List>
        ),
      };
    });
  };

  serializeGroupsForDropdown = (groups) => {
    return groups.map((group) => {
      return {
        text: group.id,
        value: group.id,
        key: group.id,
        content: (
          <List divided relaxed>
            <List.Item>
              <Image size="mini" src={group.links.avatar} avatar />
              <List.Content>
                <List.Header as="a">{group.name}</List.Header>
                <List.Description>
                  {_truncate(group.description, { length: 30 })}
                </List.Description>
              </List.Content>
            </List.Item>
          </List>
        ),
      };
    });
  };

  optionsGenerator = (suggestions) => {
    const { searchType } = this.props;
    const serializer = {
      user: this.serializeUsersForDropdown,
      group: this.serializeGroupsForDropdown,
    };
    return serializer[searchType](suggestions);
  };

  onChange = (event, data) => {
    const { handleChange, selectedMembers, searchType } = this.props;
    const { suggestions } = this.state;

    if (data.value.length === 0) return;

    const selectedValue = data.value[0];
    const memberAlreadySelected = selectedValue in selectedMembers;

    if (memberAlreadySelected) return;

    const newSelectedMember = suggestions.find((item) => item.id === selectedValue);

    const serializedSelectedMember = {
      id: newSelectedMember.id,
      type: searchType,
      avatar: newSelectedMember?.links?.avatar,
    };

    if (searchType === "group") {
      serializedSelectedMember["name"] = newSelectedMember.name; // The schema will pass the id if the name is missing
    } else {
      serializedSelectedMember["name"] = this.serializeMemberName(newSelectedMember);
    }
    selectedMembers[serializedSelectedMember.id] = serializedSelectedMember;
    handleChange(selectedMembers);
  };

  onSearchChange = async (event, { searchQuery }) => {
    const { fetchMembers } = this.props;
    try {
      this.setState({ isFetching: true });

      const cancellableSuggestions = withCancel(fetchMembers(searchQuery));
      const suggestions = await cancellableSuggestions.promise;
      this.setState({
        isFetching: false,
        suggestions: suggestions.data.hits.hits,
        error: false,
      });
    } catch (e) {
      console.error(e);
      this.setState({
        isFetching: false,
        error: true,
      });
    }
  };

  // the "search" was already done in the backend,
  // so we just return all options
  handleSearch = (options, query) => {
    return options;
  };

  render() {
    const { isFetching, error, suggestions } = this.state;
    const { placeholder } = this.props;
    return (
      <Dropdown
        selectOnBlur={false}
        error={error}
        fluid
        loading={isFetching}
        onSearchChange={this.onSearchChange}
        onChange={this.onChange}
        search={this.handleSearch}
        options={this.optionsGenerator(suggestions)}
        selection
        multiple
        value={[]}
        icon="search"
        placeholder={placeholder}
      />
    );
  }
}

MembersSearchBar.propTypes = {
  handleChange: PropTypes.func.isRequired,
  selectedMembers: PropTypes.object.isRequired,
  fetchMembers: PropTypes.func.isRequired,
  searchType: PropTypes.oneOf(["group", "user"]).isRequired,
  placeholder: PropTypes.string,
};

MembersSearchBar.defaultProps = {
  placeholder: i18next.t("Search..."),
};
