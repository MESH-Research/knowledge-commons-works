// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import React from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { List } from "semantic-ui-react";

const CreatorList = ({ creators }) => {
  return (
    <Overridable id="CreatorList.layout">
      <List horizontal>
        {creators.map((creator) => {
          return (
            <List.Item key={creator.person_or_org.name}>
              <List.Content>
                <List.Icon name="user" />
                {creator.person_or_org.name}
              </List.Content>
            </List.Item>
          );
        })}
      </List>
    </Overridable>
  );
};

CreatorList.propTypes = {
  creators: PropTypes.array.isRequired
}

export default Overridable.component("CreatorList", CreatorList);
