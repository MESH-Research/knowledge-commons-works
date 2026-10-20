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
import React, { Component, createRef } from "react";
import { http, withCancel } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Container, Grid, Header, Icon, Message, Placeholder } from "semantic-ui-react";
import { CommunityCard } from "@js/kcworks/collections/community/CommunitiesCardGroup";

/** 0-based index of the default focused card (card 2). */
const DEFAULT_CARD_INDEX = 1;

class CommunitiesCarousel extends Component {
  constructor(props) {
    super(props);

    this.rootRef = createRef();
    this.carouselTimer = null;
    this.resizeObserver = null;

    this.state = {
      data: { hits: [] },
      isLoading: true,
      canScroll: false,
    };
  }

  /** Resolve the scrollport within this instance (supports multiple carousels). */
  getViewport = () => this.rootRef.current?.querySelector(".carousel-viewport") ?? null;

  componentDidMount() {
    this.fetchData();
  }

  componentDidUpdate(_prevProps, prevState) {
    const { isLoading, data, canScroll } = this.state;
    const { autoplay, embedded } = this.props;

    if (prevState.canScroll && !canScroll) {
      this.stopCarousel();
    } else if (!prevState.canScroll && canScroll && autoplay && !isLoading) {
      this.startCarousel();
    }

    if (prevState.isLoading && !isLoading && !_isEmpty(data.hits)) {
      // Featured (center snap): wait for layout, then land on card 2.
      // Embedded (start snap): leave scroll at 0 (first card flush left).
      requestAnimationFrame(() => {
        const overflows = this.updateCanScroll();
        this.observeViewport();
        this.updateFlushClasses();
        if (!embedded) {
          this.scrollToCardIndex(DEFAULT_CARD_INDEX, "auto");
        }
        if (autoplay && overflows) {
          this.startCarousel(overflows);
        }
        requestAnimationFrame(() => this.updateFlushClasses());
      });
    }
  }

  componentWillUnmount() {
    this.cancellableFetch && this.cancellableFetch.cancel();
    this.stopCarousel();
    this.resizeObserver?.disconnect();
    this.resizeObserver = null;
    const viewport = this.getViewport();
    if (viewport && this._onViewportScroll) {
      viewport.removeEventListener("scroll", this._onViewportScroll);
    }
  }

  /**
   * Mark leftmost/rightmost visible items for hover grow direction.
   *
   * Uses visibility (not pixel-edge proximity): subpixel gaps from the
   * item-width math often miss a small epsilon, so flush-* never stuck.
   */
  updateFlushClasses = () => {
    const viewport = this.getViewport();
    if (!viewport) return;

    const items = [
      ...viewport.querySelectorAll(".carousel-item:not(.loading-placeholder)"),
    ];
    if (!items.length) return;

    const vRect = viewport.getBoundingClientRect();
    const styles = getComputedStyle(viewport);
    const padL = parseFloat(styles.paddingLeft) || 0;
    const padR = parseFloat(styles.paddingRight) || 0;
    const leftEdge = vRect.left + padL;
    const rightEdge = vRect.right - padR;

    const visible = items.filter((el) => {
      const r = el.getBoundingClientRect();
      const overlap = Math.min(r.right, rightEdge) - Math.max(r.left, leftEdge);
      return overlap > r.width * 0.5;
    });

    items.forEach((el) => {
      el.classList.remove("flush-start", "flush-end");
    });

    if (!visible.length) return;

    visible.sort(
      (a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left
    );

    const start = visible[0];
    const end = visible[visible.length - 1];
    // CTA has no hover morph; only community cards take flush classes.
    if (!start.classList.contains("carousel-find-more")) {
      start.classList.add("flush-start");
    }
    // Alone in the viewport: keep centered expand, not flush-end shift.
    if (
      visible.length > 1 &&
      end !== start &&
      !end.classList.contains("carousel-find-more")
    ) {
      end.classList.add("flush-end");
    }
  };

  /**
   * @returns {boolean} True when item count exceeds `--carousel-visible`.
   */
  updateCanScroll = () => {
    const viewport = this.getViewport();
    if (!viewport) {
      if (this.state.canScroll) {
        this.setState({ canScroll: false });
      }
      return false;
    }

    const items = viewport.querySelectorAll(".carousel-item:not(.loading-placeholder)");
    if (!items.length) {
      if (this.state.canScroll) {
        this.setState({ canScroll: false });
      }
      return false;
    }

    const visible =
      parseFloat(getComputedStyle(viewport).getPropertyValue("--carousel-visible").trim()) || 3;
    const next = items.length > visible;
    if (next !== this.state.canScroll) {
      this.setState({ canScroll: next });
    }
    return next;
  };

  observeViewport = () => {
    this.resizeObserver?.disconnect();
    const viewport = this.getViewport();
    if (!viewport) {
      return;
    }

    if (this._onViewportScroll) {
      viewport.removeEventListener("scroll", this._onViewportScroll);
    }
    this._onViewportScroll = () => this.updateFlushClasses();
    viewport.addEventListener("scroll", this._onViewportScroll, {
      passive: true,
    });

    if (typeof ResizeObserver !== "undefined") {
      this.resizeObserver = new ResizeObserver(() => {
        this.updateCanScroll();
        this.updateFlushClasses();
      });
      this.resizeObserver.observe(viewport);
    }
  };

  /**
   * Center a carousel card in the viewport.
   *
   * @param {number} index - 0-based card index.
   * @param {ScrollBehavior} [behavior="smooth"]
   */
  scrollToCardIndex = (index, behavior = "smooth") => {
    const viewport = this.getViewport();
    if (!viewport) return;

    const items = viewport.querySelectorAll(".carousel-item");
    if (!items.length) return;

    const clamped = Math.max(0, Math.min(index, items.length - 1));
    const item = items[clamped];
    const target = item.offsetLeft + item.offsetWidth / 2 - viewport.clientWidth / 2;
    const maxScroll = Math.max(0, viewport.scrollWidth - viewport.clientWidth);

    viewport.scrollTo({
      left: Math.max(0, Math.min(target, maxScroll)),
      behavior,
    });
    if (behavior === "auto") {
      this.updateFlushClasses();
    } else {
      window.setTimeout(() => this.updateFlushClasses(), 400);
    }
  };

  /**
   * Scroll the viewport by one item width (plus gap). Wraps at the ends.
   * Featured (center): forward wrap returns to card 2. Embedded (start): to 0.
   *
   * @param {number} direction - `1` for next, `-1` for previous.
   */
  scrollByItems = (direction) => {
    const viewport = this.getViewport();
    if (!viewport) return;

    const item = viewport.querySelector(".carousel-item");
    if (!item) return;

    const { embedded } = this.props;
    const styles = getComputedStyle(viewport);
    const gap = parseFloat(styles.columnGap || styles.gap) || 0;
    const step = item.getBoundingClientRect().width + gap;
    const maxScroll = viewport.scrollWidth - viewport.clientWidth;
    const epsilon = 2;

    if (direction > 0 && viewport.scrollLeft >= maxScroll - epsilon) {
      if (embedded) {
        viewport.scrollTo({ left: 0, behavior: "smooth" });
        window.setTimeout(() => this.updateFlushClasses(), 400);
      } else {
        this.scrollToCardIndex(DEFAULT_CARD_INDEX, "smooth");
      }
      return;
    }
    if (direction < 0 && viewport.scrollLeft <= epsilon) {
      viewport.scrollTo({ left: maxScroll, behavior: "smooth" });
      window.setTimeout(() => this.updateFlushClasses(), 400);
      return;
    }

    viewport.scrollBy({ left: direction * step, behavior: "smooth" });
    window.setTimeout(() => this.updateFlushClasses(), 400);
  };

  /**
   * @param {boolean} [canScrollOverride] - Use when state has not flushed yet.
   */
  setCarouselTimer = (canScrollOverride) => {
    const {
      data: { hits },
      canScroll,
    } = this.state;
    const { intervalDelay, autoplay } = this.props;
    const overflows = typeof canScrollOverride === "boolean" ? canScrollOverride : canScroll;

    this.stopCarousel();
    if (!autoplay || !overflows || _isEmpty(hits) || hits.length < 2) return;

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

  /**
   * @param {boolean} [canScrollOverride]
   */
  startCarousel = (canScrollOverride) => {
    this.setCarouselTimer(canScrollOverride);
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

  /**
   * Inline CSS vars for visible card counts per breakpoint.
   *
   * @returns {{ [key: string]: string }}
   */
  visibleCountStyle = () => {
    const { itemsPerPage, itemsPerPageTablet, itemsPerPageMobile } = this.props;
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

  /**
   * Full-width viewport with overhanging prev/next chevrons (no arrow columns).
   *
   * @param {object} options
   * @param {React.ReactNode} options.children
   * @param {string} options.viewportClass
   * @param {object} [options.pauseHandlers]
   * @param {boolean} [options.showArrows=true]
   * @returns {JSX.Element}
   */
  renderTrack = ({ children, viewportClass, pauseHandlers = {}, showArrows = true }) => (
    <div className="carousel-wrapper" {...pauseHandlers}>
      {showArrows && (
        <Icon
          className="carousel-arrow carousel-arrow-prev"
          role="button"
          name="angle left"
          size="huge"
          aria-label={i18next.t("Previous slide")}
          onClick={() => this.scrollByItems(-1)}
          onKeyDown={(event) => event.key === "Enter" && this.scrollByItems(-1)}
          tabIndex="0"
        />
      )}
      <div className={viewportClass} role="list" style={this.visibleCountStyle()}>
        {children}
      </div>
      {showArrows && (
        <Icon
          className="carousel-arrow carousel-arrow-next"
          role="button"
          name="angle right"
          size="huge"
          aria-label={i18next.t("Next slide")}
          onClick={() => this.scrollByItems(1)}
          onKeyDown={(event) => event.key === "Enter" && this.scrollByItems(1)}
          tabIndex="0"
        />
      )}
    </div>
  );

  /**
   * Featured carousel only: 1+14+1 side spacers.
   *
   * @param {React.ReactNode} track
   * @returns {JSX.Element}
   */
  renderFeaturedWidthShell = (track) => (
    <Grid container className="rel-mb-2 carousel-width-shell">
      <Grid.Column width="1" className="computer only" />
      <Grid.Column computer="14" tablet="16" mobile="16">
        {track}
      </Grid.Column>
      <Grid.Column width="1" className="computer only" />
    </Grid>
  );

  /**
   * Skeleton cards matching the SSR Jinja placeholders.
   *
   * @returns {JSX.Element[]}
   */
  renderPlaceholderItems = () => {
    const { itemsPerPage } = this.props;
    const count = Math.max(1, parseInt(itemsPerPage, 10) || 3);
    return Array.from({ length: count }, (_, index) => (
      <div
        key={`carousel-placeholder-${index}`}
        className="card-set-wrapper carousel-item loading-placeholder"
        aria-hidden="true"
      >
        <div className="ui fluid card community">
          <div className="community-card-top">
            <Placeholder fluid>
              <Placeholder.Image square />
            </Placeholder>
          </div>
          <div className="content community-card-footer">
            <Placeholder>
              <Placeholder.Header>
                <Placeholder.Line />
              </Placeholder.Header>
              <Placeholder.Paragraph>
                <Placeholder.Line />
                <Placeholder.Line />
              </Placeholder.Paragraph>
            </Placeholder>
          </div>
        </div>
      </div>
    ));
  };

  /**
   * Skeleton row in the same viewport layout as the hydrated carousel.
   *
   * @returns {JSX.Element}
   */
  renderPlaceholder = () => {
    const { title, showTitle, embedded } = this.props;
    const viewportClass = [
      "carousel-viewport",
      "pt-30",
      "pb-30",
      embedded ? "snap-start" : "",
    ]
      .filter(Boolean)
      .join(" ");

    const track = this.renderTrack({
      children: this.renderPlaceholderItems(),
      viewportClass,
      showArrows: false,
    });

    if (embedded) {
      return track;
    }

    return (
      <Container fluid className="carousel rel-pt-2 rel-pb-2 ml-0-mobile mr-0-mobile">
        {showTitle && title && (
          <Grid container className="rel-mb-0">
            <Grid.Column width="2" className="computer only" />
            <Grid.Column
              computer="12"
              tablet="16"
              mobile="16"
              widescreen="12"
              largeMonitor="12"
              className="fourteen wide large screen mb-15"
            >
              <Header as="h2">{title}</Header>
            </Grid.Column>
            <Grid.Column width="2" className="computer only" />
          </Grid>
        )}
        {this.renderFeaturedWidthShell(track)}
      </Container>
    );
  };

  /**
   * Empty-results state: message (if any) plus a full placeholder row.
   *
   * @returns {JSX.Element}
   */
  renderEmpty = () => {
    const { emptyMessage } = this.props;
    return (
      <>
        {emptyMessage && <Message icon="info" header={emptyMessage} />}
        {this.renderPlaceholder()}
      </>
    );
  };

  carouselSlides = () => {
    const { data } = this.state;
    const { defaultLogo, embedded } = this.props;

    const cards =
      data.hits?.map((community) => (
        <CommunityCard
          key={community.id}
          community={community}
          defaultLogo={defaultLogo}
          className="carousel-item"
        />
      )) ?? [];

    // Featured only: replace the end edge spacer with a collections CTA card.
    if (!embedded && cards.length > 0) {
      cards.push(
        <div
          key="carousel-find-more"
          className="card-set-wrapper carousel-item carousel-find-more"
          role="listitem"
        >
          <a className="carousel-find-more-link" href="/collections">
            {i18next.t("Find more collections...")}
          </a>
        </div>
      );
    }

    return cards;
  };

  render() {
    const { data, isLoading, canScroll } = this.state;
    const { title, itemsPerPage, showTitle, showMarkers, autoplay, embedded } = this.props;
    const slides = this.carouselSlides();
    const viewportClass = [
      "carousel-viewport",
      "pt-30",
      "pb-30",
      showMarkers ? "with-scroll-markers" : "",
      embedded ? "snap-start" : "",
      !embedded && !_isEmpty(data.hits) ? "has-find-more" : "",
    ]
      .filter(Boolean)
      .join(" ");

    const pauseHandlers =
      autoplay && canScroll
        ? {
            onFocus: this.stopCarousel,
            onBlur: this.startCarousel,
            onMouseEnter: this.stopCarousel,
            onMouseLeave: this.startCarousel,
          }
        : {};

    const track = this.renderTrack({
      children: slides,
      viewportClass,
      pauseHandlers,
      showArrows: canScroll,
    });

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
        <div ref={this.rootRef} className="communities-carousel-root">
          {isLoading && this.renderPlaceholder()}

          {!isLoading && _isEmpty(data.hits) && this.renderEmpty()}

          {!isLoading &&
            !_isEmpty(data.hits) &&
            (embedded ? (
              track
            ) : (
              <Container fluid className="carousel rel-pt-2 rel-pb-2 ml-0-mobile mr-0-mobile">
                {showTitle && title && (
                  <Grid container className="rel-mb-0">
                    <Grid.Column width="2" className="computer only" />
                    <Grid.Column
                      computer="12"
                      tablet="16"
                      mobile="16"
                      widescreen="12"
                      largeMonitor="12"
                      className="fourteen wide large screen mb-15"
                    >
                      <Header as="h2">{title}</Header>
                    </Grid.Column>
                    <Grid.Column width="2" className="computer only" />
                  </Grid>
                )}
                {this.renderFeaturedWidthShell(track)}
              </Container>
            ))}
        </div>
      </Overridable>
    );
  }
}

CommunitiesCarousel.propTypes = {
  title: PropTypes.string,
  fetchUrl: PropTypes.string.isRequired,
  intervalDelay: PropTypes.number,
  animationSpeed: PropTypes.number,
  defaultLogo: PropTypes.string.isRequired,
  /** Desktop visible count → `--carousel-visible-desktop`. */
  itemsPerPage: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  /** Tablet visible count → `--carousel-visible-tablet` (falls back to desktop). */
  itemsPerPageTablet: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  /** Mobile visible count → `--carousel-visible-mobile` (CSS default 2). */
  itemsPerPageMobile: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  showUploadBtn: PropTypes.bool,
  showTitle: PropTypes.bool,
  showMarkers: PropTypes.bool,
  autoplay: PropTypes.bool,
  /** Compact mount for section slots (titles live in the page template). */
  embedded: PropTypes.bool,
  emptyMessage: PropTypes.string,
};

CommunitiesCarousel.defaultProps = {
  title: "",
  intervalDelay: 10000,
  animationSpeed: 800,
  itemsPerPage: "3",
  itemsPerPageTablet: undefined,
  itemsPerPageMobile: undefined,
  showUploadBtn: true,
  showTitle: true,
  showMarkers: true,
  autoplay: true,
  embedded: false,
  emptyMessage: "",
};

export default Overridable.component("InvenioCommunities.CommunitiesCarousel", CommunitiesCarousel);
