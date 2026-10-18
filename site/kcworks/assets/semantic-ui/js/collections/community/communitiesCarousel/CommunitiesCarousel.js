/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
 *
 * Modified by Mesh Research as part of Knowledge Commons Works
 * Copyright (C) 2024-2026 Mesh Research
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/kcworks/i18next";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { http, withCancel } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Container, Grid, Header, Icon, Item, Placeholder } from "semantic-ui-react";
import { CommunityCard } from "@js/kcworks/collections/community/CommunitiesCardGroup";
import CarouselItem from "./CarouselItem";

class CommunitiesCarousel extends Component {
  constructor(props) {
    super(props);

    this.carouselTimer = null;

    this.state = {
      data: { hits: [] },
      isLoading: true,
    };
  }

  /** SUI Column doesn't forward refs; the column itself is the scrollport. */
  getViewport = () => document.querySelector("#communities-carousel .carousel-viewport");

  componentDidMount() {
    this.fetchData();
  }

  componentDidUpdate(_prevProps, prevState) {
    const { isLoading, data } = this.state;
    if (prevState.isLoading && !isLoading && !_isEmpty(data.hits)) {
      this.startCarousel();
    }
  }

  componentWillUnmount() {
    this.cancellableFetch && this.cancellableFetch.cancel();
    this.stopCarousel();
  }

  /**
   * Scroll the viewport by one item width (plus gap). Wraps at the ends.
   *
   * @param {number} direction - `1` for next, `-1` for previous.
   */
  scrollByItems = (direction) => {
    const viewport = this.getViewport();
    if (!viewport) return;

    const item = viewport.querySelector(".carousel-item");
    if (!item) return;

    const styles = getComputedStyle(viewport);
    const gap = parseFloat(styles.columnGap || styles.gap) || 0;
    const step = item.getBoundingClientRect().width + gap;
    const maxScroll = viewport.scrollWidth - viewport.clientWidth;
    const epsilon = 2;

    if (direction > 0 && viewport.scrollLeft >= maxScroll - epsilon) {
      viewport.scrollTo({ left: 0, behavior: "smooth" });
      return;
    }
    if (direction < 0 && viewport.scrollLeft <= epsilon) {
      viewport.scrollTo({ left: maxScroll, behavior: "smooth" });
      return;
    }

    viewport.scrollBy({ left: direction * step, behavior: "smooth" });
  };

  setCarouselTimer = () => {
    const {
      data: { hits },
    } = this.state;
    const { intervalDelay } = this.props;

    this.stopCarousel();
    if (_isEmpty(hits) || hits.length < 2) return;

    this.carouselTimer = setInterval(() => {
      this.scrollByItems(1);
    }, intervalDelay);
  };

  stopCarousel = () => {
    if (this.carouselTimer) {
      clearInterval(this.carouselTimer);
      this.carouselTimer = null;
    }
  };

  startCarousel = () => {
    this.setCarouselTimer();
  };

  fetchData = async () => {
    const { fetchUrl } = this.props;
    this.cancellableFetch = withCancel(http.get(fetchUrl));
    try {
      const response = await this.cancellableFetch.promise;
      this.setState({ data: response.data.hits, isLoading: false });
    } catch (error) {
      console.error(error);
      this.setState({ isLoading: false });
    }
  };

  renderPlaceholder = () => {
    const { title } = this.props;
    return (
      <Container fluid className="rel-pt-2 rel-pb-2 ml-0-mobile mr-0-mobile">
        <Grid container className="carousel-header-container">
          <Grid.Column width="2" />
          <Grid.Column width="12">
            <Header as="h2" className="rel-mb-1">
              {title}
            </Header>
          </Grid.Column>
          <Grid.Column width="2" />
        </Grid>
        <Grid container className="carousel-items-container">
          <Grid.Column width="2" />
          <Grid.Column width="12">
            <Item.Group>
              <Item>
                <Item.Image>
                  <Placeholder>
                    <Placeholder.Image square />
                  </Placeholder>
                </Item.Image>

                <Item.Content>
                  <Item.Header className="mt-5 rel-mb-2">
                    <Placeholder>
                      <Placeholder.Header>
                        <Placeholder.Line />
                      </Placeholder.Header>
                    </Placeholder>
                  </Item.Header>

                  <Item.Description>
                    <Placeholder>
                      <Placeholder.Paragraph>
                        <Placeholder.Line />
                        <Placeholder.Line />
                        <Placeholder.Line />
                      </Placeholder.Paragraph>
                    </Placeholder>
                  </Item.Description>
                </Item.Content>
              </Item>
            </Item.Group>
          </Grid.Column>
          <Grid.Column width="2" />
        </Grid>
      </Container>
    );
  };

  carouselSlides = () => {
    const { data } = this.state;
    const { defaultLogo, showUploadBtn } = this.props;

    return data.hits?.map((community) => (
      <CommunityCard
        key={community.id}
        community={community}
        defaultLogo={defaultLogo}
        className="carousel-item"
      />
    ));
  };

  render() {
    const { data, isLoading } = this.state;
    const { title, itemsPerPage } = this.props;
    const slides = this.carouselSlides();

    return (
      <Overridable
        id="InvenioCommunities.CommunitiesCarousel.layout"
        data={data}
        title={title}
        carouselSlides={slides}
        stopCarousel={this.stopCarousel}
        startCarousel={this.startCarousel}
        scrollByItems={this.scrollByItems}
        itemsPerPage={itemsPerPage}
      >
        <>
          {isLoading && this.renderPlaceholder()}

          {!isLoading && !_isEmpty(data.hits) && (
            <Container fluid className="carousel rel-pt-2 rel-pb-2 ml-0-mobile mr-0-mobile">
              <Grid container className="rel-mb-0">
                <Grid.Column width="2" className="tablet computer only" />
                <Grid.Column
                  computer="12"
                  tablet="12"
                  mobile="16"
                  widescreen="12"
                  largeMonitor="12"
                  className="twelve wide large screen mb-15"
                >
                  <Header as="h2">{title}</Header>
                </Grid.Column>
                <Grid.Column width="2" className="tablet computer only" />
              </Grid>

              <Grid
                container
                className={"rel-mb-2 carousel-wrapper"}
                onFocus={this.stopCarousel}
                onBlur={this.startCarousel}
                onMouseEnter={this.stopCarousel}
                onMouseLeave={this.startCarousel}
              >
                <Grid.Column
                  width="1"
                  className="pr-0 rel-pb-2"
                  verticalAlign="middle"
                  textAlign="left"
                >
                  <Icon
                    className="carousel-arrow"
                    inverted
                    role="button"
                    name="angle left"
                    size="huge"
                    aria-label={i18next.t("Previous slide")}
                    onClick={() => this.scrollByItems(-1)}
                    onKeyDown={(event) => event.key === "Enter" && this.scrollByItems(-1)}
                    tabIndex="0"
                  />
                </Grid.Column>
                <Grid.Column
                  width="14"
                  className="carousel-viewport"
                  role="list"
                  style={{
                    "--carousel-visible-desktop": String(parseInt(itemsPerPage, 10) || 3),
                  }}
                >
                  {slides}
                </Grid.Column>

                <Grid.Column
                  width="1"
                  className="pl-0 rel-pb-2"
                  verticalAlign="middle"
                  textAlign="right"
                >
                  <Icon
                    className="carousel-arrow"
                    inverted
                    role="button"
                    name="angle right"
                    size="huge"
                    aria-label={i18next.t("Next slide")}
                    onClick={() => this.scrollByItems(1)}
                    onKeyDown={(event) => event.key === "Enter" && this.scrollByItems(1)}
                    tabIndex="0"
                  />
                </Grid.Column>
              </Grid>
            </Container>
          )}
        </>
      </Overridable>
    );
  }
}

CommunitiesCarousel.propTypes = {
  title: PropTypes.string.isRequired,
  fetchUrl: PropTypes.string.isRequired,
  intervalDelay: PropTypes.number.isRequired,
  animationSpeed: PropTypes.number,
  defaultLogo: PropTypes.string.isRequired,
  itemsPerPage: PropTypes.string.isRequired,
  showUploadBtn: PropTypes.bool,
};

CommunitiesCarousel.defaultProps = {
  animationSpeed: 800,
  showUploadBtn: true,
};

export default Overridable.component("InvenioCommunities.CommunitiesCarousel", CommunitiesCarousel);
