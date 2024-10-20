import React, { useContext, useState } from "react";
import { i18next } from "@translations/invenio_communities/i18next";
import _upperFirst from "lodash/upperFirst";
import { DateTime } from "luxon";
import PropTypes from "prop-types";
import { Image } from "react-invenio-forms";
import { Button, Grid, Item, Label, Table } from "semantic-ui-react";
import { MembersContext } from "@js/invenio_communities/api/members/MembersContextProvider";
import { SearchResultsRowCheckbox } from "@js/invenio_communities/members/components/bulk_actions/SearchResultsRowCheckbox";
import { RoleDropdown, VisibilityDropdown } from "@js/invenio_communities/members/components/dropdowns";
import { ModalContext } from "@js/invenio_communities/members/components/modal_manager";
import { modalModeEnum } from "@js/invenio_communities/members/components/RemoveMemberModal";
import { parametrize } from "react-overridable";
import { memberVisibilityTypes } from "@js/invenio_communities/members/members";

const timestampToRelativeTime = (timestamp) =>
  DateTime.fromISO(timestamp).setLocale(i18next.language).toRelative();

const ManagerMembersResultItem  = ({ result, config, community }) => {

  const [innerResult, setInnerResult] = useState(result);
  const membersContext = useContext(MembersContext);
  const membershipRelativeTimestamp = timestampToRelativeTime(innerResult.created);
  const memberVisibility = innerResult.visible ? i18next.t("Public") : i18next.t("Hidden");
  const { api } = membersContext;

  const groupName = community.custom_fields?.['kcr:commons_group_name'] || community.metadata.title;
  const memberName = innerResult.member.name.replace(/knowledgeCommons---\d+\|/, `${groupName} group `);

  const updateMemberRole = (data, value) => {
    setInnerResult({ ...innerResult, ...{ role: value } });
  };

  const updateMemberVisibility = (data, value) => {
    // visibility can not be changed from hidden to public by other members
    const newValueIsPublic = !!value;
    const isEditingSelf = innerResult.is_current_user;
    const memberCanChangeVisibilityAfterUpdate = newValueIsPublic || isEditingSelf;

    const updatedPermissions = {
      ...innerResult.permissions,
      can_update_visible: memberCanChangeVisibilityAfterUpdate,
    };

    setInnerResult({ ...innerResult, visible: value, permissions: updatedPermissions });
  };

  const openLeaveOrRemoveModal = (openModalCallback, isRemoving = true) => {
    const { member } = result;

    const modalAction = () => api.removeMember(member);
    const modalMode = isRemoving ? modalModeEnum.remove : modalModeEnum.leave;

    openModalCallback({ modalMode, modalAction });
  };

  return (
    <Table.Row>
      <Table.Cell>
        <Grid textAlign="left" verticalAlign="middle">
          <Grid.Column>
            <Item
              className={innerResult.is_current_user ? "flex align-no-checkbox" : "flex"}
              key={innerResult.id}
            >
              {!innerResult.is_current_user && (
                <SearchResultsRowCheckbox rowId={innerResult.id} data={innerResult} />
              )}
              <Image
                src={innerResult.member.avatar}
                avatar
                className={innerResult.is_current_user ? "" : "rel-ml-1"}
              />
              <Item.Content className="ml-10">
                <Item.Header
                  className={`flex align-items-center ${
                    !innerResult.member.description ? "mt-5" : ""
                  }`}
                >
                  <b className="mr-10">{memberName}</b>

                  {innerResult.member.type === "group" && (
                    <Label size="tiny" className="mr-10">
                      {i18next.t("Group")}
                    </Label>
                  )}
                  {innerResult.is_current_user && (
                    <Label size="tiny" className="primary">
                      {i18next.t("You")}
                    </Label>
                  )}
                </Item.Header>
                {innerResult.member.description && (
                  <Item.Meta>
                    <div className="truncate-lines-1">
                      {innerResult.member.description}
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
        {innerResult.permissions.can_update_visible ? (
          <VisibilityDropdown
            visibilityTypes={config.visibility}
            successCallback={updateMemberVisibility}
            action={api.updateVisibility}
            currentValue={innerResult.visible}
            resource={innerResult}
            label={i18next.t("Visibility") + " " + memberVisibility}
          />
        ) : (
          memberVisibility
        )}
      </Table.Cell>

      <Table.Cell data-label={i18next.t("Role")}>
        {innerResult.permissions.can_update_role ? (
          <RoleDropdown
            roles={config.rolesCanUpdate}
            successCallback={updateMemberRole}
            action={api.updateRole}
            currentValue={innerResult.role}
            resource={innerResult}
            label={i18next.t("Role") + " " + innerResult.role}
          />
        ) : (
          _upperFirst(innerResult.role)
        )}
      </Table.Cell>

      <ModalContext.Consumer>
        {({ openModal }) => (
          <Table.Cell data-label={i18next.t("Actions")}>
            <div>
              {innerResult.permissions.can_leave && (
                <Button
                  negative
                  size="tiny"
                  labelPosition="left"
                  icon="log out"
                  fluid
                  className="fluid-computer-only"
                  compact
                  content={i18next.t("Leave...")}
                  onClick={() => openLeaveOrRemoveModal(openModal, false)}
                />
              )}
              {innerResult.permissions.can_delete && (
                <Button
                  size="tiny"
                  labelPosition="left"
                  icon="user delete"
                  fluid
                  className="fluid-computer-only"
                  compact
                  content={i18next.t("Remove...")}
                  onClick={() => openLeaveOrRemoveModal(openModal, true)}
                />
              )}
            </div>
          </Table.Cell>
        )}
      </ModalContext.Consumer>
    </Table.Row>
  );
}

ManagerMembersResultItem.propTypes = {
  result: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
};

// FIXME: This is a workaround to access the community
// object without overriding the root files
// invenio_communities/members/members/member_view/index.js and
// invenio_communities/members/members/manager_view/index.js
// where the containers are defined. We just override this componennt

const dataAttr = document.getElementById("community-members-search-root")?.dataset;
const communitiesRolesCanUpdate = dataAttr ? JSON.parse(dataAttr.communitiesRolesCanUpdate) : {};
const permissions = dataAttr ? JSON.parse(dataAttr.permissions) : {};
const community = dataAttr ? JSON.parse(dataAttr.community) : {};

const ManagerMembersResultItemWithConfig = parametrize(ManagerMembersResultItem, {
  config: {
    rolesCanUpdate: communitiesRolesCanUpdate,
    visibility: memberVisibilityTypes,
    permissions: permissions,
  },
  community: community,
});

export { ManagerMembersResultItemWithConfig, ManagerMembersResultItem };