/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2023 Northwestern University.
 *
 * Modified by Mesh Research as part of Knowledge Commons Works
 * Copyright (C) 2024-2026 Mesh Research
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

/**
 * Walk `community.parent` like `community_breadcrumb_items` (root → leaf).
 *
 * @param {object} community
 * @returns {{ id: string, title: string, slug: string }[]}
 */
export function getAncestorCommunities(community) {
  const ancestors = [];
  let current = community?.parent;
  while (current) {
    ancestors.push({
      id: current.id,
      title: current.metadata?.title || "",
      slug: current.slug || "",
    });
    current = current.parent;
  }
  return ancestors.reverse();
}

/**
 * Resolve groups URL base from page config (same destination as `KC_GROUPS_URL_BASE`).
 *
 * @returns {string}
 */
export function getKcGroupsUrlBase() {
  const domain =
    document.getElementById("main-nav-menu")?.dataset?.kcWordpressDomain ||
    document.querySelector("[data-kc-wordpress-domain]")?.dataset
      ?.kcWordpressDomain;
  return domain ? `https://${domain}/groups/` : "";
}

/**
 * KC group linked to a collection (`kcr:commons_group_*`), as on the detail header.
 *
 * @param {object} community
 * @returns {{ id: string, name: string, href: string } | null}
 */
export function getCommonsGroup(community) {
  const id = community?.custom_fields?.["kcr:commons_group_id"];
  if (!id) {
    return null;
  }
  const name = community.custom_fields?.["kcr:commons_group_name"] || id;
  const base = getKcGroupsUrlBase();
  return {
    id,
    name,
    href: base ? `${base}${id}` : "",
  };
}

class CommunityCard extends Component {
  render() {
    const { className, community, defaultLogo } = this.props;
    const isCarousel = Boolean(className?.includes("carousel-item"));
    const title = community.metadata?.title || "";
    const rawDescription = community.metadata?.description || "";
    const description =
      rawDescription ||
      (isCarousel ? "A Knowledge Commons Works collection." : "");
    const collectionHref = `/collections/${community.slug}`;
    const ancestors = isCarousel ? getAncestorCommunities(community) : [];
    const commonsGroup = isCarousel ? getCommonsGroup(community) : null;
    const hasFinePrint = Boolean(commonsGroup) || ancestors.length > 0;
    const headerBg = community.theme?.style?.mainHeaderBackgroundColor;
    const headerFg = community.theme?.style?.primaryTextColor;
    const themeStyle =
      isCarousel && (headerBg || headerFg)
        ? {
            ...(headerBg ? { "--community-header-bg": headerBg } : {}),
            ...(headerFg ? { "--community-header-fg": headerFg } : {}),
          }
        : undefined;

    return (
      <div className={`card-set-wrapper ${className || ""}`.trim()}>
        <Card fluid className="community" style={themeStyle}>
          <div className="community-card-top">
            <div className="community-card-logo">
              <a href={collectionHref} tabIndex={isCarousel ? -1 : undefined}>
                <Image
                  wrapped
                  centered
                  ui={false}
                  src={community.links.logo}
                  alt={`logo for ${title} collection`}
                  fallbackSrc={defaultLogo || "/static/images/square-placeholder.png"}
                  loadFallbackFirst
                />
              </a>
            </div>
            {isCarousel && (
              <div className="community-card-overlay">
                <div className="desc-full">{description}</div>
              </div>
            )}
          </div>
          <Card.Content className="community-card-footer">
            <Card.Header as="a" href={collectionHref}>
              {isCarousel ? title : _truncate(title, { length: 40 })}
            </Card.Header>
            {!isCarousel && description && (
              <Card.Description className="desc-compact">
                <div className="truncate-lines-2">{description}</div>
              </Card.Description>
            )}
            {isCarousel && hasFinePrint && (
              <div className="community-card-footer-swap">
                <div className="parents">
                  {commonsGroup && (
                    <span className="kc-group">
                      <i className="users icon fitted" aria-hidden="true" />{" "}
                      {commonsGroup.href ? (
                        <a href={commonsGroup.href}>{commonsGroup.name}</a>
                      ) : (
                        <span>{commonsGroup.name}</span>
                      )}
                    </span>
                  )}
                  {commonsGroup && ancestors.length > 0 && (
                    <span className="parents-sep"> · </span>
                  )}
                  {ancestors.length > 0 && (
                    <>
                      <span className="parents-label">Part of </span>
                      {ancestors.map((item, index) => (
                        <React.Fragment key={item.id || item.slug || index}>
                          {index > 0 && (
                            <span className="parents-divider"> › </span>
                          )}
                          <a href={`/collections/${item.slug}`}>{item.title}</a>
                        </React.Fragment>
                      ))}
                    </>
                  )}
                </div>
              </div>
            )}
          </Card.Content>
        </Card>
      </div>
    );
  }
}

CommunityCard.propTypes = {
  community: PropTypes.object.isRequired,
  defaultLogo: PropTypes.string.isRequired,
  className: PropTypes.string,
};

CommunityCard.defaultProps = {
  className: "",
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

  visibleCountStyle = () => {
    const { itemsPerPage, itemsPerPageTablet, itemsPerPageMobile } = this.props;
    if (itemsPerPage == null || itemsPerPage === "") {
      return undefined;
    }
    const desktop = Math.max(1, parseInt(itemsPerPage, 10) || 3);
    const style = {
      "--carousel-visible-desktop": String(desktop),
    };
    if (itemsPerPageTablet != null && itemsPerPageTablet !== "") {
      style["--carousel-visible-tablet"] = String(
        Math.max(1, parseInt(itemsPerPageTablet, 10) || desktop)
      );
    }
    if (itemsPerPageMobile != null && itemsPerPageMobile !== "") {
      style["--carousel-visible-mobile"] = String(
        Math.max(1, parseInt(itemsPerPageMobile, 10) || 2)
      );
    }
    return style;
  };

  renderCards() {
    const { data } = this.state;
    const { defaultLogo, carouselCards } = this.props;

    return data.hits.map((community) => (
      <CommunityCard
        key={community.id}
        community={community}
        defaultLogo={defaultLogo}
        className={carouselCards ? "carousel-item" : ""}
      />
    ));
  }

  render() {
    const { isLoading, data } = this.state;
    const { emptyMessage, carouselCards } = this.props;
    return (
      <PlaceholderLoader isLoading={isLoading}>
        {data.hits.length === 0 ? (
          <EmptyMessage message={emptyMessage} />
        ) : carouselCards ? (
          <div className="carousel-card-grid" style={this.visibleCountStyle()}>
            {this.renderCards()}
          </div>
        ) : (
          <Card.Group doubling stackable itemsPerRow={5} className="community-frontpage-cards">
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
  /** Use carousel-item cards in a wrapping `.carousel-card-grid`. */
  carouselCards: PropTypes.bool,
  itemsPerPage: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  itemsPerPageTablet: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  itemsPerPageMobile: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

CommunitiesCardGroup.defaultProps = {
  carouselCards: false,
  itemsPerPage: undefined,
  itemsPerPageTablet: undefined,
  itemsPerPageMobile: undefined,
};

export default CommunitiesCardGroup;
export { CommunityCard };
