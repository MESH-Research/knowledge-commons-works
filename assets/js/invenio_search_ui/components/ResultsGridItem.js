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
import { Card, Label } from "semantic-ui-react";

export const ResultsGridItem = ({ result }) => {
  const metadata = result.metadata;
  return (
    <Card fluid href={_get(result, "links.html", "#")}>
      <Card.Content>
        <Card.Header>{metadata.title}</Card.Header>
        <Card.Description>
          {_truncate(
            metadata.contributors
              .map((contributor) => contributor.name)
              .join("; "),
            { length: 200 }
          )}
        </Card.Description>
      </Card.Content>
      <Card.Content extra>
        {metadata.keywords &&
          metadata.keywords.map((keyword, idx) => (
            <Label key={idx}>{keyword}</Label>
          ))}
      </Card.Content>
    </Card>
  );
};
