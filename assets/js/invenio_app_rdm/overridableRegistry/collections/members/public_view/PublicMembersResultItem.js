import { i18next } from "@translations/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import { Grid, Item, Label, Table } from "semantic-ui-react";
import { parametrize } from "react-overridable";

class PublicMemberPublicViewResultItem extends Component {
  render() {
    const { result } = this.props;
    const avatar = result.member.avatar;
    return (
      <Table.Row>
        <Table.Cell>
          <Grid textAlign="left" verticalAlign="middle">
            <Grid.Column>
              <Item className="flex" key={result.id}>
                <Image
                  src={avatar}
                  avatar
                  fallbackSrc="/static/images/square-placeholder.png"
                />
                <Item.Content className="ml-10">
                  <Item.Header className={!result.member.description ? "mt-5" : ""}>
                    <b>{result.member.name}</b>
                    {result.member.type === "group" && (
                      <Label className="ml-10">{i18next.t("Group")}</Label>
                    )}
                  </Item.Header>
                  {result.member.description && (
                    <Item.Meta>
                      <div className="truncate-lines-1">
                        {result.member.description}
                      </div>
                    </Item.Meta>
                  )}
                </Item.Content>
              </Item>
            </Grid.Column>
          </Grid>
        </Table.Cell>
      </Table.Row>
    );
  }
}

PublicMemberPublicViewResultItem.propTypes = {
  result: PropTypes.object.isRequired,
};

// FIXME: This is a workaround to access the community
// object without overriding the root files
// invenio_communities/members/members/public_view/index.js
// where the containers are defined. We just override this componennt

const dataAttr = document.getElementById("community-members-search-root")?.dataset;
const community = dataAttr ? JSON.parse(dataAttr.community) : {};

const PublicMembersResultsItemWithCommunity = parametrize(PublicMemberPublicViewResultItem, {community: community});

PublicMembersResultsItemWithCommunity.propTypes = {
  result: PropTypes.object.isRequired,
};

export { PublicMembersResultsItemWithCommunity, PublicMemberPublicViewResultItem };