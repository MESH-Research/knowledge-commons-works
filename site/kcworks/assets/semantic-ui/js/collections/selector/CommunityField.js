// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021-2022 Graz University of Technology.
//
// Customized for Knowledge Commons Works
// Copyright (C) 2024 Mesh Research
//
// Invenio-RDM-Records and Knowledge Commons Works are free software;
// you can redistribute and/or modify them under the terms of the MIT License;
// see LICENSE file for more details.

import React, { useState, useContext, useRef } from "react";
import { connect, useStore } from "react-redux";
import { i18next } from "@translations/invenio_modular_deposit_form/i18next";
import PropTypes from "prop-types";
import { Trans } from "react-i18next";
import { Image } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Button, Icon, Form, Grid, Header, Item, Message } from "semantic-ui-react";

import { FormUIStateContext } from "@js/invenio_modular_deposit_form/FormUIStateManager";
import { getReadableFields } from "@js/invenio_modular_deposit_form/utils";
import { CommunitySelectionModalFromDeposit } from "./CommunitySelectionModal/CommunitySelectionModal";

export const changeSelectedCommunity = (community) => {
  return async (dispatch) => {
    dispatch({
      type: "SET_COMMUNITY",
      payload: { community },
    });
    window.setTimeout(() => {
      document.querySelectorAll(`.community-field-button`)[0].focus();
    }, 50);
  };
};

const CommunityListItem = ({
  community,
  changeSelectedCommunity,
  isInReview,
  isPublished,
  isNewVersion,
  focusAddButtonHandler,
  setModalOpen,
  modalOpen,
  selectionButtonDisabled,
  permissionsPerField,
  triggerButtonRef,
}) => {
  return (
    <Item>
      <Item.Image
        size="tiny"
        className="community-image mini"
        src={community.links?.logo || `/api/communities/${community.id}/logo`}
        fallbackSrc="/static/images/square-placeholder.png"
      />
      <Item.Content verticalAlign="middle">
        <span>{community.metadata.title}</span>
      </Item.Content>

      <div className="community-item-actions">
        <AddEditCommunityButton
          classnames={""}
          community={community}
          changeSelectedCommunity={changeSelectedCommunity}
          isInReview={isInReview}
          isPublished={isPublished}
          isNewVersion={isNewVersion}
          focusAddButtonHandler={focusAddButtonHandler}
          setModalOpen={setModalOpen}
          modalOpen={modalOpen}
          selectionButtonDisabled={selectionButtonDisabled}
          permissionsPerField={permissionsPerField}
          triggerButtonRef={triggerButtonRef}
        />
        {community && (
          <RemoveCommunityButton
            clasnames="ml-10"
            community={community}
            changeSelectedCommunity={changeSelectedCommunity}
            selectionButtonDisabled={selectionButtonDisabled}
          />
        )}
      </div>
    </Item>
  );
};

CommunityListItem.propTypes = {
  community: PropTypes.object.isRequired,
};

const AddEditCommunityButton = ({
  classnames,
  community,
  changeSelectedCommunity,
  focusAddButtonHandler,
  isInReview,
  isNewVersion,
  isPublished,
  setModalOpen,
  modalOpen,
  selectionButtonDisabled,
  permissionsPerField,
  triggerButtonRef,
}) => {
  const showSubmissionWarning = !isInReview && !community && !isPublished && !isNewVersion;

  return (
    <CommunitySelectionModalFromDeposit
      permissionsPerField={permissionsPerField}
      modalHeader={i18next.t("Select a collection")}
      onCommunityChange={(community) => {
        changeSelectedCommunity(community);
        focusAddButtonHandler();
        setModalOpen(false);
      }}
      onModalChange={(value) => {
        value === false && focusAddButtonHandler();
        setModalOpen(value);
      }}
      modalOpen={modalOpen}
      chosenCommunity={community}
      displaySelected
      trigger={
        <Overridable id="InvenioRdmRecords.CommunityHeader.CommunitySelectionButton.Container">
          <Button
            ref={triggerButtonRef}
            aria-haspopup="dialog"
            aria-expanded={modalOpen}
            className={`community-field-button add-button ${classnames}`}
            disabled={selectionButtonDisabled}
            onClick={() => setModalOpen(true)}
            name="setting"
            id="community-selector"
            type="button"
            floated={!community ? "left" : ""}
          >
            {community ? i18next.t("Change") : i18next.t("Select a collection")}
          </Button>
        </Overridable>
      }
      focusAddButtonHandler={focusAddButtonHandler}
      showSubmissionWarning={showSubmissionWarning}
      setModalOpen={setModalOpen}
    />
  );
};

AddEditCommunityButton.propTypes = {
  community: PropTypes.object.isRequired,
  changeSelectedCommunity: PropTypes.func.isRequired,
  focusAddButtonHandler: PropTypes.func.isRequired,
  setModalOpen: PropTypes.func.isRequired,
  modalOpen: PropTypes.bool.isRequired,
  selectionButtonDisabled: PropTypes.bool.isRequired,
  permissionsPerField: PropTypes.object,
  triggerButtonRef: PropTypes.object,
};

AddEditCommunityButton.defaultProps = {
  permissionsPerField: undefined,
};

const RemoveCommunityButton = ({
  community,
  changeSelectedCommunity,
  classnames,
  selectionButtonDisabled,
}) => {
  return (
    <Overridable
      id="InvenioRdmRecords.CommunityHeader.RemoveCommunityButton.Container"
      community={community}
    >
      <Button
        aria-label={i18next.t("Remove item")}
        className={`close-btn mt-0 ml-12 ${classnames ?? ""}`}
        icon
        onClick={() => changeSelectedCommunity(null)}
        disabled={selectionButtonDisabled}
      >
        <Icon name="close" />
      </Button>
    </Overridable>
  );
};

RemoveCommunityButton.propTypes = {
  community: PropTypes.object.isRequired,
  changeSelectedCommunity: PropTypes.func.isRequired,
  selectionButtonDisabled: PropTypes.bool.isRequired,
};

const usePerFieldPermissions = (community, permissionsPerField, isPublished, isNewVersion) => {
  let removalRestricted = false;
  const currentCommunityPermissions = permissionsPerField?.[community?.slug]?.policy;
  let AffectedFields = [];
  if (currentCommunityPermissions) {
    AffectedFields = Array.isArray(currentCommunityPermissions)
      ? currentCommunityPermissions
      : Object.keys(currentCommunityPermissions);
    if (AffectedFields.some((field) => field.startsWith("parent.communities.default"))) {
      removalRestricted = true;
      AffectedFields = AffectedFields.filter(
        (field) => !field.startsWith("parent.communities.default")
      );
    }
    const [readableFields, readableFieldsWithArrays] = getReadableFields(AffectedFields);
    AffectedFields = [...readableFields, ...readableFieldsWithArrays];
  }

  const restrictionHeader = i18next.t(
    `${
      isPublished ? "This work's primary " : "The selected "
    }collection restricts editing of some information`
  );
  const restrictionMessage = !isPublished ? (
    <p>
      {i18next.t("After publishing your work to the ")} <i>{community?.metadata?.title}</i>{" "}
      {i18next.t(
        " collection you will not be able to change these metadata fields without the approval and assistance of the collection administrators:"
      )}
    </p>
  ) : (
    <p>
      {i18next.t("Since this work was published to the ")} <i>{community?.metadata?.title}</i>{" "}
      {i18next.t(
        " collection, you cannot to change these metadata fields without the approval and assistance of the collection administrators:"
      )}
    </p>
  );

  const removalRestrictionHeader = i18next.t(
    "The " +
      community?.metadata?.title +
      " collection does not allow removing works from the collection once they are published."
  );
  const removalRestrictionMessage = i18next.t(
    "This work is restricted from being removed from the " +
      community?.metadata?.title +
      " collection"
  );

  return {
    removalRestricted,
    restrictionHeader,
    restrictionMessage,
    removalRestrictionHeader,
    removalRestrictionMessage,
    AffectedFields,
  };
};

const InReviewMessage = ({ communityTitle }) => {
  return (
    <Message info icon>
      <Icon name="info circle" />
      <Message.Content>
        <Message.Header>
          {i18next.t(
            "This work is currently in publication review by the {{communityTitle}} collection curators.",
            { communityTitle: communityTitle }
          )}
        </Message.Header>
        <Trans
          defaults="You cannot change the collection for this work until the review is complete or you cancel the review request from your <0>requests inbox</0>"
          components={[
            <a
              href="/me/requests"
              target="_blank"
              rel="noopener noreferrer"
              aria-label={i18next.t("my requests")}
            />,
          ]}
        />
      </Message.Content>
    </Message>
  );
};

InReviewMessage.propTypes = {
  communityTitle: PropTypes.string.isRequired,
};

const RemovalRestrictedMessage = ({ removalRestrictionHeader, removalRestrictionMessage }) => {
  return (
    <Message info icon>
      <Icon name="info circle" />
      <Message.Content>
        <Message.Header>{removalRestrictionHeader}</Message.Header>
        {removalRestrictionMessage}
      </Message.Content>
    </Message>
  );
};

RemovalRestrictedMessage.propTypes = {
  removalRestrictionHeader: PropTypes.string.isRequired,
  removalRestrictionMessage: PropTypes.string.isRequired,
};

const RestrictedFieldsMessage = ({
  restrictionHeader,
  restrictionMessage,
  restrictedFields,
  community,
}) => {
  return (
    <Message info icon>
      <Icon name="info circle" />
      <Message.Content>
        <Message.Header>{restrictionHeader}</Message.Header>
        {restrictionMessage}
        <ul>
          {restrictedFields.map((field) => (
            <li key={field}>{field}</li>
          ))}
        </ul>
        <p>
          <Trans
            defaults="See the collection's <0>curation policy</0> page for more information."
            components={[
              <a
                href={`/collections/${community?.slug}/curation-policy`}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={i18next.t("curation policy")}
              />,
            ]}
          />
        </p>
      </Message.Content>
    </Message>
  );
};

RestrictedFieldsMessage.propTypes = {
  restrictionHeader: PropTypes.string.isRequired,
  restrictionMessage: PropTypes.string.isRequired,
  restrictedFields: PropTypes.array.isRequired,
  community: PropTypes.object,
};

RestrictedFieldsMessage.defaultProps = {
  community: undefined,
};

const CommunityFieldComponent = ({
  classnames = "",
  community = undefined,
  changeSelectedCommunity,
  showCommunitySelectionButton,
  disableCommunitySelectionButton,
  label = i18next.t("Community submission"),
}) => {
  const [modalOpen, setModalOpen] = useState();
  const triggerButtonRef = useRef(null);
  const store = useStore();
  const isPublished = store.getState().deposit.record?.is_published;
  const isInReview = store.getState().deposit.record?.status === "in_review";
  const isNewVersion = store.getState().deposit.record?.status === "new_version_draft";
  const recordLink = store.getState().deposit.record?.links?.record_html;
  const communities = store.getState().deposit.record?.parent?.communities?.entries;
  const { permissionsPerField } = useContext(FormUIStateContext);
  const otherCommunities =
    community && communities ? communities.filter((c) => c.id !== community.id) : [];

  const focusAddButtonHandler = () => {
    // SUI Button exposes .focus() on the component instance
    triggerButtonRef.current?.focus?.();
  };

  const selectionButtonDisabled =
    disableCommunitySelectionButton ||
    !showCommunitySelectionButton ||
    isInReview ||
    isNewVersion ||
    isPublished;
  const selectionButtonShown = showCommunitySelectionButton && !isPublished && !isNewVersion;

  const {
    removalRestricted,
    restrictionHeader,
    restrictionMessage,
    removalRestrictionHeader,
    removalRestrictionMessage,
    AffectedFields: restrictedFields,
  } = usePerFieldPermissions(community, permissionsPerField, isPublished, isNewVersion);

  const changeOnDetailPageMessage = (
    <Trans
      defaults="Add or change collections for a published work from the work's <0>detail page</0>"
      components={[
        <a
          href={`${recordLink}`}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="detail page"
        />,
      ]}
    />
  );

  const buttonArgs = {
    community,
    changeSelectedCommunity,
    isInReview,
    isPublished,
    isNewVersion,
    focusAddButtonHandler,
    setModalOpen,
    modalOpen,
    selectionButtonDisabled,
    permissionsPerField,
    triggerButtonRef,
  };

  return (
    <div className={`invenio-field-wrapper community-field ${classnames}`}>
      <Form.Field>
        <label htmlFor="community-selector" className="field-label-class invenio-field-label">
          {label}
          <Icon name="ml-12 mr-0 users" />
        </label>
        {community && !selectionButtonShown && (
          <div className="description">{changeOnDetailPageMessage}</div>
        )}
        {community && !isInReview && (
          <div className="description">
            {i18next.t(
              "This work will be submitted for review to the collection below. (Not yet submitted.)"
            )}
          </div>
        )}
      </Form.Field>
      <Form.Group className="mb-0">
        {community ? (
          <Form.Field width={16}>
            <Item.Group divided>
              <CommunityListItem {...buttonArgs} />
              {otherCommunities.map((c) => (
                <CommunityListItem key={c.id} {...{ ...buttonArgs, community: c }} />
              ))}
            </Item.Group>
          </Form.Field>
        ) : (
          <>
            <Form.Field width={6} className="right-btn-column">
              {community && !selectionButtonShown ? null : (
                <AddEditCommunityButton classnames="" {...buttonArgs} />
              )}
            </Form.Field>
            <Form.Field width={11} className="communities-helptext-wrapper">
              <label htmlFor="community-selector" className="helptext">
                {selectionButtonShown
                  ? i18next.t("Do you want to submit this deposit for publication by a collection?")
                  : changeOnDetailPageMessage}
              </label>
            </Form.Field>
          </>
        )}
      </Form.Group>

      {isInReview && <InReviewMessage communityTitle={community?.metadata?.title} />}

      {removalRestricted && (
        <RemovalRestrictedMessage
          removalRestrictionHeader={removalRestrictionHeader}
          removalRestrictionMessage={removalRestrictionMessage}
        />
      )}

      {restrictedFields?.length > 0 && (
        <RestrictedFieldsMessage
          restrictionHeader={restrictionHeader}
          restrictionMessage={restrictionMessage}
          restrictedFields={restrictedFields}
          community={community}
        />
      )}
    </div>
  );
};

CommunityFieldComponent.propTypes = {
  imagePlaceholderLink: PropTypes.string,
  community: PropTypes.object,
  disableCommunitySelectionButton: PropTypes.bool.isRequired,
  showCommunitySelectionButton: PropTypes.bool.isRequired,
  showCommunityHeader: PropTypes.bool.isRequired,
  changeSelectedCommunity: PropTypes.func.isRequired,
  label: PropTypes.string,
};

CommunityFieldComponent.defaultProps = {
  imagePlaceholderLink: undefined,
  community: undefined,
  label: "Community submission",
};

const mapStateToProps = (state) => ({
  community: state.deposit.editorState.selectedCommunity,
  disableCommunitySelectionButton: state.deposit.editorState.ui.disableCommunitySelectionButton,
  showCommunitySelectionButton: state.deposit.editorState.ui.showCommunitySelectionButton,
  showCommunityHeader: state.deposit.editorState.ui.showCommunityHeader,
});

const mapDispatchToProps = (dispatch) => ({
  changeSelectedCommunity: (community) => dispatch(changeSelectedCommunity(community)),
});

export const CommunityField = connect(mapStateToProps, mapDispatchToProps)(CommunityFieldComponent);
