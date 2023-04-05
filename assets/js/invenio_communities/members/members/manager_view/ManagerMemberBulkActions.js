import { SearchResultsBulkActions } from "@js/invenio_communities/members/components/bulk_actions/SearchResultsBulkActions";
import { ErrorMessage } from "@js/invenio_communities/members/components/ErrorMessage";
import { CommunityMembersApi } from "../../../api/members/api";
import { BulkActionsContext } from "@js/invenio_communities/members/components/bulk_actions/context";
import { RadioSelection } from "@js/invenio_communities/members/components/bulk_actions/RadioSelection";
import { SelectedMembers } from "@js/invenio_communities/members/components/bulk_actions/SelectedMembers";
import _mapValues from "lodash/mapValues";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_communities/i18next";
import { Button, Form, Modal } from "semantic-ui-react";
import { Trans } from "react-i18next";
import { withState } from "react-searchkit";
import { withCancel } from "react-invenio-forms";

class ManagerMemberBulkActionsCmp extends Component {
  constructor(props) {
    super(props);
    const { community } = this.props;

    this.membersApi = new CommunityMembersApi(community);

    this.state = {
      modalOpen: false,
      currentAction: undefined,
      role: undefined,
      visible: undefined,
      selectedMembers: {},
    };
  }

  componentWillUnmount() {
    this.cancellableAction && this.cancellableAction.cancel();
  }

  static contextType = BulkActionsContext;

  bulkAction = (action) => {
    action();
  };

  get bulkActions() {
    const { roles, visibilities, permissions } = this.props;
    return [
      {
        key: 1,
        value: "change_role",
        text: i18next.t("Change roles"),
        renderOnActive: () => (
          <Form>
            <RadioSelection
              options={roles}
              label={i18next.t("Role")}
              onOptionChangeCallback={this.handleChangeRole}
              permissions={permissions}
            />
          </Form>
        ),
        action: this.membersApi.bulkUpdateRoles,
        actionParam: "role",
      },
      {
        key: 2,
        value: "change_visibility",
        text: i18next.t("Change visibilities"),
        action: this.membersApi.bulkUpdateVisibilities,
        actionParam: "visible",
        renderOnActive: () => (
          <Form>
            <RadioSelection
              options={visibilities}
              label={i18next.t("Visibility")}
              onOptionChangeCallback={this.handleChangeVisibility}
              permissions={permissions}
            />
          </Form>
        ),
      },
      {
        key: 3,
        value: "remove_from_community",
        text: i18next.t("Remove from community"),
        action: this.membersApi.bulkRemoveMembers,
      },
    ];
  }

  handleChangeRole = (role) => {
    this.setState({ role: role });
  };

  handleChangeVisibility = (visible) => {
    this.setState({ visible: visible === "public" });
  };

  updateSelectedMembers = (members) => {
    this.setState({ selectedMembers: members });
  };

  handleChooseCurrentAction = (value, selectedMembers, selectedCount) => {
    const serializeSelected = _mapValues(selectedMembers, ({ data }) => ({
      ...data.member,
    }));

    this.updateSelectedMembers(serializeSelected);
    this.setState({ currentAction: value });
    this.handleModalOpen();
  };

  handleModalClose = () => this.setState({ modalOpen: false });

  handleModalOpen = () => this.setState({ modalOpen: true });

  handleActionClick = async () => {
    const { selectedMembers } = this.state;
    const { updateQueryState, currentQueryState } = this.props;
    const { setAllSelected } = this.context;

    const actionToPerform = this.currentAction.action;
    // eslint-disable-next-line react/destructuring-assignment
    const actionParameter = this.state[this.currentAction.actionParam];

    const members = Object.entries(selectedMembers).map(([memberId, member]) => member);

    this.setState({ loading: true });

    this.cancellableAction = withCancel(actionToPerform(members, actionParameter));
    try {
      await this.cancellableAction.promise;

      this.setState({ loading: false });
      this.handleModalClose();
      this.setState({ role: undefined, visible: undefined });

      updateQueryState(currentQueryState);
      setAllSelected(false, true);
    } catch (error) {
      if (error === "UNMOUNTED") return;

      this.setState({ loading: false, error: error });
    }
  };

  get currentAction() {
    const { currentAction } = this.state;

    return this.bulkActions.find((option) => {
      return option.value === currentAction;
    });
  }

  render() {
    const { modalOpen, selectedMembers, loading, error } = this.state;
    const selectedCount = Object.keys(selectedMembers).length;

    const currentActionRender =
      this.currentAction?.renderOnActive && this.currentAction.renderOnActive();

    const currentActionText = this.currentAction?.text;

    const actionDisabled =
      loading ||
      selectedCount === 0 ||
      // eslint-disable-next-line react/destructuring-assignment
      !this.state[this.currentAction.actionParam] === undefined;

    return (
      <>
        <SearchResultsBulkActions
          bulkDropdownOptions={this.bulkActions}
          optionSelectionCallback={this.handleChooseCurrentAction}
        />
        <Modal
          onClose={this.handleModalClose}
          onOpen={this.handleModalOpen}
          closeOnDimmerClick={false}
          open={modalOpen}
          role="dialog"
          aria-labelledby="bulk-actions-modal-header"
        >
          <Modal.Header as="h2" id="bulk-actions-modal-header">
            {currentActionText}
          </Modal.Header>
          <Modal.Content>
            {error && <ErrorMessage error={error} />}
            <SelectedMembers
              updateSelectedMembers={this.updateSelectedMembers}
              selectedMembers={selectedMembers}
            />
            {currentActionRender}
          </Modal.Content>
          <Modal.Actions>
            <Button
              content={i18next.t("Cancel")}
              labelPosition="left"
              icon="cancel"
              loading={loading}
              disabled={loading}
              floated="left"
              onClick={this.handleModalClose}
            />
            <Trans key="communityInviteMembersSelected" count={selectedCount}>
              You have selected {{ selectedCount }} users
            </Trans>
            <Button
              content={currentActionText}
              labelPosition="left"
              loading={loading}
              disabled={actionDisabled}
              icon="checkmark"
              primary
              onClick={this.handleActionClick}
            />
          </Modal.Actions>
        </Modal>
      </>
    );
  }
}

ManagerMemberBulkActionsCmp.propTypes = {
  community: PropTypes.object.isRequired,
  roles: PropTypes.array.isRequired,
  visibilities: PropTypes.array.isRequired,
  permissions: PropTypes.object.isRequired,
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
};

export const ManagerMemberBulkActions = withState(ManagerMemberBulkActionsCmp);
