/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import _truncate from "lodash/truncate";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Button, Grid, Header, Item } from "semantic-ui-react";
import GeoPattern from "geopattern";

class CarouselItem extends Component {
  render() {
    const { community, defaultLogo, className, showUploadBtn } = this.props;
    const self_link = community.links.self_html.replace(
      "communities",
      "collections"
    );

    const pattern = GeoPattern.generate(encodeURI(community.slug));

    return (
      <Overridable
        id="InvenioCommunities.CarouselItem.layout"
        community={community}
        defaultLogo={defaultLogo}
        className={className}
      >
        <Item
          className={`carousel flex align-items-center ${className}`}
          key={community.id}
        >
          <Image
            size="small"
            src={community.links.logo}
            fallbackSrc={pattern.toDataUri()}
          />
          <Item.Content as={Grid}>
            <Grid.Column computer="12" tablet="16" className="pl-0 pb-0">
              <Item.Header stackable className="rel-pb-1">
                <Header as="a" size="medium" href={self_link}>
                  {community.metadata.title}
                </Header>
              </Item.Header>
              <Item.Description
                content={_truncate(community.metadata.description, {
                  length: 300,
                })}
              />
            </Grid.Column>

            <Grid.Column
              computer="4"
              tablet="16"
              className="buttons pl-0 pb-0"
            >
              <div className="buttons-wrapper">
              <Button
                size="mini"
                href={self_link}
                content={i18next.t("Browse")}
                className="browse-btn"
              />
              {showUploadBtn && (
                <Button
                  size="mini"
                  // icon="upload"
                  // labelPosition="left"
                  primary
                  href={`/uploads/new?community=${community.slug}`}
                  content={i18next.t("Contribute")}
                  className="contribute-btn"
                />
              )}</div>
            </Grid.Column>
          </Item.Content>
        </Item>
      </Overridable>
    );
  }
}

CarouselItem.propTypes = {
  community: PropTypes.object.isRequired,
  defaultLogo: PropTypes.string.isRequired,
  className: PropTypes.string,
  showUploadBtn: PropTypes.bool,
};

CarouselItem.defaultProps = {
  className: "",
  showUploadBtn: true,
};

export default Overridable.component(
  "InvenioCommunities.CarouselItem",
  CarouselItem
);
