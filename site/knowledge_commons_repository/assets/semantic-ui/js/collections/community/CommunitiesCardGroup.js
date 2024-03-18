/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2023 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import _truncate from "lodash/truncate";
import React, { Component } from "react";
import { Image, withCancel } from "react-invenio-forms";
import { Card, Grid, Message, Placeholder } from "semantic-ui-react";
import { http } from "react-invenio-forms";
import PropTypes from "prop-types";
import GeoPattern from "geopattern";

const PlaceholderLoader = ({ size, isLoading, children, ...props }) => {
  const PlaceholderItem = () => (
    <Grid.Column width={3}>
      <Placeholder>
        <Placeholder.Image square />
      </Placeholder>
      <Placeholder>
        <Placeholder.Paragraph>
          <Placeholder.Line length="medium" />
          <Placeholder.Line length="short" />
        </Placeholder.Paragraph>
      </Placeholder>
    </Grid.Column>
  );
  let numberOfHeader = [];
  for (let i = 0; i < size; i++) {
    numberOfHeader.push(<PlaceholderItem key={i} />);
  }

  if (!isLoading) {
    return children;
  }
  return (
    <Grid columns="equal" stackable>
      {numberOfHeader}
    </Grid>
  );
};

PlaceholderLoader.propTypes = {
  size: PropTypes.number,
  isLoading: PropTypes.bool.isRequired,
  children: PropTypes.node.isRequired,
};

PlaceholderLoader.defaultProps = {
  size: 5,
};

const EmptyMessage = ({ message }) => {
  return <Message icon="info" header={message} />;
};

EmptyMessage.propTypes = {
  message: PropTypes.string.isRequired,
};

class CommunityCard extends Component {
  render() {
    const { community, defaultLogo } = this.props;

    const pattern = GeoPattern.generate(community.slug);

    return (
      <Card fluid href={`/collections/${community.slug}`}>
        <Image
          wrapped
          centered
          ui={false}
          src={community.links.logo}
          fallbackSrc={pattern.toDataUri()}
          loadFallbackFirst
        />
        <Card.Content>
          <Card.Header>
            {_truncate(community.metadata.title, { length: 40 })}
          </Card.Header>
          {community.metadata.description && (
            <Card.Description>
              <div className="truncate-lines-2">{community.metadata.description}</div>
            </Card.Description>
          )}
        </Card.Content>
      </Card>
    );
  }
}

CommunityCard.propTypes = {
  community: PropTypes.object.isRequired,
  defaultLogo: PropTypes.string.isRequired,
};

class CommunitiesCardGroup extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: false,
      data: { hits: [] },
    };
  }

  componentDidMount() {
    this.fetchData();
  }

  componentWillUnmount() {
    this.cancellableFetch && this.cancellableFetch.cancel();
  }

  fetchData = async () => {
    const { fetchDataUrl } = this.props;
    this.setState({ isLoading: true });
    this.cancellableFetch = withCancel(http.get(fetchDataUrl));

    try {
      const response = await this.cancellableFetch.promise;

      this.setState({ data: response.data.hits, isLoading: false });
    } catch (error) {
      // TODO: handle error response
    }
  };

  renderCards() {
    const { data } = this.state;
    const { defaultLogo } = this.props;

    return data.hits.map((community) => {
      return (
        <CommunityCard
          key={community.id}
          community={community}
          defaultLogo={defaultLogo}
        />
      );
    });
  }

  render() {
    const { isLoading, data } = this.state;
    const { emptyMessage } = this.props;
    return (
      <PlaceholderLoader isLoading={isLoading}>
        {data.hits.length === 0 ? (
          <EmptyMessage message={emptyMessage} />
        ) : (
          <Card.Group
            doubling
            stackable
            itemsPerRow={5}
            className="community-frontpage-cards"
          >
            {this.renderCards()}
          </Card.Group>
        )}
      </PlaceholderLoader>
    );
  }
}

CommunitiesCardGroup.propTypes = {
  fetchDataUrl: PropTypes.string.isRequired,
  defaultLogo: PropTypes.string.isRequired,
  emptyMessage: PropTypes.string.isRequired,
};

export default CommunitiesCardGroup;
