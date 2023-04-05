/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_communities/i18next";
import { http } from "react-invenio-forms";
import { withCancel } from "react-invenio-forms";
import { Transition, Container, Grid, Header, Item, Icon } from "semantic-ui-react";
import CarouselItem from "./CarouselItem";
import Overridable from "react-overridable";
import _isEmpty from "lodash/isEmpty";

class CommunitiesCarousel extends Component {
  constructor(props) {
    super(props);

    this.state = {
      data: { hits: [] },
      activeIndex: 0,
      animationDirection: "left",
      carouselTimer: null,
    };
  }

  componentDidMount() {
    this.fetchData();
  }

  componentWillUnmount() {
    this.cancellableFetch && this.cancellableFetch.cancel();
    this.stopCarousel();
  }

  getDataIndex = (index) => {
    const {
      data: { hits },
    } = this.state;
    if (index > hits.length - 1) return 0;
    if (index < 0) return hits.length - 1;
    return index;
  };

  runCarousel = async (newIndex) => {
    const { activeIndex } = this.state;
    let animationDirection = newIndex < activeIndex ? "right" : "left";
    await this.setState({ animationDirection });
    this.setState({ activeIndex: this.getDataIndex(newIndex) });
  };

  setCarouselTimer = () => {
    const {
      data: { hits: length },
      activeIndex,
    } = this.state;
    const { intervalDelay } = this.props;
    this.setState({
      carouselTimer: setInterval(() => {
        length && this.runCarousel(activeIndex + 1);
      }, intervalDelay),
    });
  };

  // Pause carousel when user focuses elements in the container
  stopCarousel = () => {
    const { carouselTimer } = this.state;
    clearInterval(carouselTimer);
  };
  startCarousel = () => {
    this.setCarouselTimer();
  };

  fetchData = async () => {
    const { fetchUrl } = this.props;
    this.cancellableFetch = withCancel(http.get(fetchUrl));

    try {
      const response = await this.cancellableFetch.promise;
      this.setState({ data: response.data.hits });
      this.setCarouselTimer();
    } catch (error) {
      console.error(error);
    }
  };

  render() {
    const { data, animationDirection, activeIndex } = this.state;
    const { title, animationSpeed, defaultLogo } = this.props;

    const carouselSlides = data.hits?.map(
      (community, index) =>
        index === activeIndex && (
          <CarouselItem
            community={community}
            defaultLogo={defaultLogo}
            key={community.id}
          />
        )
    );

    return (
      <Overridable
        id="InvenioCommunities.CommunitiesCarousel.layout"
        data={data}
        animationDirection={animationDirection}
        activeIndex={activeIndex}
        title={title}
        animationSpeed={animationSpeed}
        carouselSlides={carouselSlides}
        stopCarousel={this.stopCarousel}
        startCarousel={this.startCarousel}
        runCarousel={this.runCarousel}
      >
        {!_isEmpty(data.hits) && (
          <Container
            fluid
            className="carousel rel-pt-2 rel-pb-2 ml-0-mobile mr-0-mobile"
          >
            {title && (
              <Container className="rel-mb-1">
                <Header as="h2">{title}</Header>
              </Container>
            )}

            <Grid container onFocus={this.stopCarousel} onBlur={this.startCarousel}>
              <Grid.Column
                width="2"
                className="pr-0"
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
                  onClick={() => this.runCarousel(activeIndex - 1)}
                  onKeyDown={(event) =>
                    event.key === "Enter" && this.runCarousel(activeIndex - 1)
                  }
                  tabIndex="0"
                />
              </Grid.Column>

              <Grid.Column width="12">
                <Transition.Group
                  as={Item.Group}
                  className="flex align-items-center justify-center"
                  duration={animationSpeed}
                  animation={`carousel-slide ${animationDirection}`}
                  directional
                >
                  {carouselSlides}
                </Transition.Group>
              </Grid.Column>

              <Grid.Column
                width="2"
                className="pl-0"
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
                  onClick={() => this.runCarousel(activeIndex + 1)}
                  onKeyDown={(event) =>
                    event.key === "Enter" && this.runCarousel(activeIndex + 1)
                  }
                  tabIndex="0"
                />
              </Grid.Column>
            </Grid>
          </Container>
        )}
      </Overridable>
    );
  }
}

CommunitiesCarousel.propTypes = {
  title: PropTypes.string.isRequired,
  fetchUrl: PropTypes.string.isRequired,
  intervalDelay: PropTypes.number.isRequired,
  animationSpeed: PropTypes.number.isRequired,
  defaultLogo: PropTypes.string.isRequired,
};

export default Overridable.component(
  "InvenioCommunities.CommunitiesCarousel",
  CommunitiesCarousel
);
