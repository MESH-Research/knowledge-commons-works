/*
 * This file is part of Invenio.
 * Copyright (C) 2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import _get from "lodash/get";
import _truncate from "lodash/truncate";
import React from "react";
import { Item, Label } from "semantic-ui-react";

export const ResultsListItem = ({ result }) => {
  const metadata = result.metadata;
  return (
    <Item href={_get(result, "links.html", "#")}>
      <Item.Content>
        <Item.Header>{metadata.title}</Item.Header>
        <Item.Description>
          {_truncate(
            metadata.contributors
              .map((contributor) => contributor.name)
              .join("; "),
            { length: 200 }
          )}
        </Item.Description>
        <Item.Extra>
          {metadata.keywords &&
            metadata.keywords.map((keyword, idx) => (
              <Label key={idx}>{keyword}</Label>
            ))}
        </Item.Extra>
      </Item.Content>
    </Item>
  );
};
