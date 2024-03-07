import React from "react";
import { Card } from "semantic-ui-react";
import PropTypes from "prop-types";

export const ResultsGridItemTemplate = ({ result }) => {
  return (
    <Card fluid href={`/communities/${result.slug}`}>
      <Card.Content>
        <Card.Header>{result.metadata.title}</Card.Header>
        <Card.Description>
          <div className="truncate-lines-2">{result.metadata.description}</div>
        </Card.Description>
      </Card.Content>
    </Card>
  );
};

ResultsGridItemTemplate.propTypes = {
  result: PropTypes.object.isRequired,
};
