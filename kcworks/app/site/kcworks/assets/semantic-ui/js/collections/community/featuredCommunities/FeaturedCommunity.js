import React, { Component } from "react";
import { Grid, Segment, Header } from "semantic-ui-react";
import PropTypes from "prop-types";
import { Image } from "react-invenio-forms";
import GeoPattern from "geopattern";

export default class FeaturedCommunity extends Component {
  render() {
    const {
      computerColumnWidth,
      mobileColumnWidth,
      tabletColumnWidth,
      widescreenColumnWidth,
      community,
    } = this.props;

    const self_link = community.links.self_html.replace(
      "communities",
      "collections"
    );

    const pattern = GeoPattern.generate(encodeURI(community.slug));

    return (
      <Grid.Column
        mobile={mobileColumnWidth}
        tablet={tabletColumnWidth}
        widescreen={widescreenColumnWidth}
        computer={computerColumnWidth}
        textAlign="center"
      >
        <Segment compact className="m-auto">
          <a href={self_link}>
            <div className="featured-community">
              <Image
                className="m-auto"
                src={community.links.logo}
                fallbackSrc={pattern.toDataUri()}
              />
              <Header as="h3">{community.metadata.title}</Header>
            </div>
          </a>
        </Segment>
      </Grid.Column>
    );
  }
}

FeaturedCommunity.propTypes = {
  computerColumnWidth: PropTypes.number.isRequired,
  mobileColumnWidth: PropTypes.number.isRequired,
  tabletColumnWidth: PropTypes.number.isRequired,
  widescreenColumnWidth: PropTypes.number.isRequired,
  community: PropTypes.object.isRequired,
};
