import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import { Grid, Item, Label, Table } from "semantic-ui-react";

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
                    {result.member.is_group && (
                      <Label className="ml-10">{i18next.t("Group")}</Label>
                    )}
                  </Item.Header>
                  {result.member.description && (
                    <Item.Meta>
                      <div
                        className="truncate-lines-1"
                        dangerouslySetInnerHTML={{
                          __html: result.member.description,
                        }}
                      />
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

export function PublicMembersResultsItem({ result }) {
  return <PublicMemberPublicViewResultItem result={result} />;
}

PublicMembersResultsItem.propTypes = {
  result: PropTypes.object.isRequired,
};
