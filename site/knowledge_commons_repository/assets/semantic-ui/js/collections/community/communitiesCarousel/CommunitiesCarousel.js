/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { http, withCancel } from "react-invenio-forms";
import Overridable from "react-overridable";
import {
  Container,
  Grid,
  Header,
  Icon,
  Item,
  Placeholder,
  Transition,
} from "semantic-ui-react";
import CarouselItem from "./CarouselItem";

class CommunitiesCarousel extends Component {
  constructor(props) {
    super(props);

    this.state = {
      data: { hits: [] },
      activeIndex: 0,
      animationDirection: "left",
      carouselTimer: null,
      isLoading: true,
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
    const { itemsPerPage } = this.props;
    const {
      data: { hits },
    } = this.state;
    const i = index * parseInt(itemsPerPage);
    if (i > hits.length - 1) return 0;
    if (i < 0) return hits.length - 1;
    return i;
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
      this.setState({ isLoading: false });
    } catch (error) {
      console.error(error);
      this.setState({ isLoading: false });
    }
  };

  renderPlaceholder = () => {
    const { title } = this.props;
    return (
      <Container fluid className="rel-pt-2 rel-pb-2 ml-0-mobile mr-0-mobile">
        <Container>
          <Header as="h2" className="rel-mb-1">
            {title}
          </Header>
        </Container>
        <Grid container>
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
    const { data, activeIndex } = this.state;
    const { defaultLogo, itemsPerPage, showUploadBtn } = this.props;

    const sliceEnd = parseInt(activeIndex) + parseInt(itemsPerPage);

    const carouselSlides = data.hits
      ?.slice(activeIndex, sliceEnd)
      .map((community) => (
        <CarouselItem
          community={community}
          defaultLogo={defaultLogo}
          key={community.id}
          showUploadBtn={showUploadBtn}
        />
      ));

    return carouselSlides;
  };

  render() {
    const { data, animationDirection, activeIndex, isLoading } = this.state;
    const { title, animationSpeed, itemsPerPage } = this.props;

    return (
      <Overridable
        id="InvenioCommunities.CommunitiesCarousel.layout"
        data={data}
        animationDirection={animationDirection}
        activeIndex={activeIndex}
        title={title}
        animationSpeed={animationSpeed}
        carouselSlides={this.carouselSlides()}
        stopCarousel={this.stopCarousel}
        startCarousel={this.startCarousel}
        runCarousel={this.runCarousel}
        itemsPerPage={itemsPerPage}
      >
        <>
          {isLoading && this.renderPlaceholder()}

          {!isLoading && !_isEmpty(data.hits) && (
            <Container
              fluid
              className="carousel rel-pt-2 rel-pb-2 ml-0-mobile mr-0-mobile"
            >
              <Container className="rel-mb-1">
                <Header as="h2">{title}</Header>
              </Container>

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
                    {this.carouselSlides()}
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
        </>
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
  itemsPerPage: PropTypes.string.isRequired,
  showUploadBtn: PropTypes.bool,
};

CommunitiesCarousel.defaultProps = {
  showUploadBtn: true,
};

export default Overridable.component(
  "InvenioCommunities.CommunitiesCarousel",
  CommunitiesCarousel
);
