import { i18next } from "@translations/invenio_communities/i18next";
import _upperFirst from "lodash/upperFirst";
import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import { Button, Grid, Item, Label, Table } from "semantic-ui-react";
import { MembersContext } from "../../../api/members/MembersContextProvider";
import { SearchResultsRowCheckbox } from "../../components/bulk_actions/SearchResultsRowCheckbox";
import { RoleDropdown, VisibilityDropdown } from "../../components/dropdowns";
import { ModalContext } from "../../components/modal_manager";
import { modalModeEnum } from "../../components/RemoveMemberModal";

const timestampToRelativeTime = (timestamp) =>
  DateTime.fromISO(timestamp).setLocale(i18next.language).toRelative();

export class ManagerMembersResultItem extends Component {
  constructor(props) {
    super(props);
    const { result } = props;
    this.state = { result: result };
  }

  static contextType = MembersContext;

  updateMemberRole = (data, value) => {
    const { result } = this.state;
    this.setState({ result: { ...result, ...{ role: value } } });
  };

  updateMemberVisibility = (data, value) => {
    const { result } = this.state;
    // visibility can not be changed from hidden to public by other members
    const newValueIsPublic = !!value;
    const isEditingSelf = result.is_current_user;
    const memberCanChangeVisibilityAfterUpdate = newValueIsPublic || isEditingSelf;

    const updatedPermissions = {
      ...result.permissions,
      can_update_visible: memberCanChangeVisibilityAfterUpdate,
    };

    this.setState({
      result: { ...result, visible: value, permissions: updatedPermissions },
    });
  };

  openLeaveOrRemoveModal = (openModalCallback, isRemoving = true) => {
    const { result } = this.props;
    const { api } = this.context;

    const { member } = result;

    const modalAction = () => api.removeMember(member);
    const modalMode = isRemoving ? modalModeEnum.remove : modalModeEnum.leave;

    openModalCallback({ modalMode, modalAction });
  };

  render() {
    const { config } = this.props;
    const { result } = this.state;
    const { api } = this.context;
    const membershipRelativeTimestamp = timestampToRelativeTime(result.created);
    const memberVisibility = result.visible ? i18next.t("Public") : i18next.t("Hidden");
    return (
      <Table.Row>
        <Table.Cell>
          <Grid textAlign="left" verticalAlign="middle">
            <Grid.Column>
              <Item
                className={result.is_current_user ? "flex align-no-checkbox" : "flex"}
                key={result.id}
              >
                {!result.is_current_user && (
                  <SearchResultsRowCheckbox rowId={result.id} data={result} />
                )}
                <Image
                  src={result.member.avatar}
                  avatar
                  className={result.is_current_user ? "" : "rel-ml-1"}
                />
                <Item.Content className="ml-10">
                  <Item.Header
                    className={`flex align-items-center ${
                      !result.member.description ? "mt-5" : ""
                    }`}
                  >
                    <b className="mr-10">{result.member.name}</b>

                    {result.member.type === "group" && (
                      <Label size="tiny" className="mr-10">
                        {i18next.t("Group")}
                      </Label>
                    )}
                    {result.is_current_user && (
                      <Label size="tiny" className="primary">
                        {i18next.t("You")}
                      </Label>
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

        <Table.Cell
          aria-label={i18next.t("Member since") + " " + membershipRelativeTimestamp}
          data-label={i18next.t("Member since")}
        >
          {membershipRelativeTimestamp}
        </Table.Cell>

        <Table.Cell
          aria-label={i18next.t("Visibility") + " " + memberVisibility}
          data-label={i18next.t("Visibility")}
        >
          {result.permissions.can_update_visible ? (
            <VisibilityDropdown
              visibilityTypes={config.visibility}
              successCallback={this.updateMemberVisibility}
              action={api.updateVisibility}
              currentValue={result.visible}
              resource={result}
              label={i18next.t("Visibility") + " " + memberVisibility}
            />
          ) : (
            memberVisibility
          )}
        </Table.Cell>

        <Table.Cell data-label={i18next.t("Role")}>
          {result.permissions.can_update_role ? (
            <RoleDropdown
              roles={config.rolesCanUpdate}
              successCallback={this.updateMemberRole}
              action={api.updateRole}
              currentValue={result.role}
              resource={result}
              label={i18next.t("Role") + " " + result.role}
            />
          ) : (
            _upperFirst(result.role)
          )}
        </Table.Cell>

        <ModalContext.Consumer>
          {({ openModal }) => (
            <Table.Cell data-label={i18next.t("Actions")}>
              <div>
                {result.permissions.can_leave && (
                  <Button
                    negative
                    size="tiny"
                    labelPosition="left"
                    icon="log out"
                    fluid
                    className="fluid-computer-only"
                    compact
                    content={i18next.t("Leave...")}
                    onClick={() => this.openLeaveOrRemoveModal(openModal, false)}
                  />
                )}
                {result.permissions.can_delete && (
                  <Button
                    size="tiny"
                    labelPosition="left"
                    icon="user delete"
                    fluid
                    className="fluid-computer-only"
                    compact
                    content={i18next.t("Remove...")}
                    onClick={() => this.openLeaveOrRemoveModal(openModal, true)}
                  />
                )}
              </div>
            </Table.Cell>
          )}
        </ModalContext.Consumer>
      </Table.Row>
    );
  }
}

ManagerMembersResultItem.propTypes = {
  result: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
};
