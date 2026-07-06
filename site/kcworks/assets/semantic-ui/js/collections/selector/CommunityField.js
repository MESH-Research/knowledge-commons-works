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

import { i18next } from "@translations/invenio_modular_deposit_form/i18next";
import PropTypes from "prop-types";
import React, { useState, useContext } from "react";
import { connect, useStore } from "react-redux";
import { Trans } from "react-i18next";
import { Image } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Button, Icon, Form, Grid, Header, Message } from "semantic-ui-react";

import { FormUIStateContext } from "@js/invenio_modular_deposit_form/FormUIStateManager";
import { getReadableFields } from "@js/invenio_modular_deposit_form/utils";
import { CommunitySelectionModal } from "./CommunitySelectionModal/CommunitySelectionModal";

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

const CommunityListItem = ({ community }) => {
  return (
    <>
      <Grid.Column width={2}>
        <Image
          size="tiny"
          className="community-header-logo"
          src={community.links?.logo || "/static/images/square-placeholder.png"}
          fallbackSrc="/static/images/square-placeholder.png"
        />
      </Grid.Column>
      <Grid.Column width={14}>
        <Header size="small">{community.metadata.title}</Header>
      </Grid.Column>
    </>
  );
};

CommunityListItem.propTypes = {
  community: PropTypes.object.isRequired,
};

const AddEditCommunityButton = ({
  community,
  changeSelectedCommunity,
  focusAddButtonHandler,
  setModalOpen,
  modalOpen,
  selectionButtonDisabled,
  permissionsPerField,
}) => {
  return (
    <CommunitySelectionModal
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
            className="community-field-button add-button"
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
};

AddEditCommunityButton.defaultProps = {
  permissionsPerField: undefined,
};

const RemoveCommunityButton = ({
  community,
  changeSelectedCommunity,
  selectionButtonDisabled,
}) => {
  return (
    <Overridable
      id="InvenioRdmRecords.CommunityHeader.RemoveCommunityButton.Container"
      community={community}
    >
      <Button
        aria-label={i18next.t("Remove item")}
        className="close-btn mt-0"
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

const usePerFieldPermissions = (
  community,
  permissionsPerField,
  isPublished,
  isNewVersion
) => {
  let removalRestricted = false;
  const currentCommunityPermissions = permissionsPerField?.[community?.slug]?.policy;
  let AffectedFields = [];
  if (currentCommunityPermissions) {
    AffectedFields = Array.isArray(currentCommunityPermissions)
      ? currentCommunityPermissions
      : Object.keys(currentCommunityPermissions);
    if (
      AffectedFields.some((field) => field.startsWith("parent.communities.default"))
    ) {
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
      {i18next.t("After publishing your work to the ")}{" "}
      <i>{community?.metadata?.title}</i>{" "}
      {i18next.t(
        " collection you will not be able to change these metadata fields without the approval and assistance of the collection administrators:"
      )}
    </p>
  ) : (
    <p>
      {i18next.t("Since this work was published to the ")}{" "}
      <i>{community?.metadata?.title}</i>{" "}
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

const RemovalRestrictedMessage = ({
  removalRestrictionHeader,
  removalRestrictionMessage,
}) => {
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

const PublicationReviewWarning = () => {
  return (
    <Message warning icon className="deposit-publication-review-warning">
      <Icon name="warning sign" />
      <Message.Content>
        <Message.Header>
          <Trans
            defaults="You may want to submit to collections <0>after</0> your work is published"
            components={[<i />]}
          />
        </Message.Header>
        <p>
          <Trans
            defaults="Submitting to a collection is optional. If you submit your work for publication by a collection now, your upload <0>will not be publicly visible</0> until it has been approved by that collection's curators."
            components={[<b />]}
          />
        </p>
        <p>
          <Trans
            defaults="Most collections are <0>not curated by the KCWorks team</0> , and collection curators may take a significant amount of time to review your work."
            components={[<b />]}
          />
        </p>
        <p>
          <Trans
            defaults="You can submit your work to a collection <0>after publication</0> from the sidebar of your published record's detail page"
            components={[<b />]}
          />
        </p>
      </Message.Content>
    </Message>
  );
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
  community = undefined,
  changeSelectedCommunity,
  imagePlaceholderLink,
  showCommunitySelectionButton,
  disableCommunitySelectionButton,
  label = "Community submission",
}) => {
  const [modalOpen, setModalOpen] = useState();
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
    document.querySelectorAll(`.community-field-button`)[0].focus();
  };

  const selectionButtonDisabled =
    disableCommunitySelectionButton ||
    !showCommunitySelectionButton ||
    isInReview ||
    isNewVersion ||
    isPublished;
  const selectionButtonShown =
    showCommunitySelectionButton && !isPublished && !isNewVersion;

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

  return (
    <>
      <Form.Field>
        <label
          htmlFor="community-selector"
          className="field-label-class invenio-field-label"
        >
          <Icon name="users" />
          {label}
        </label>
      </Form.Field>
      <Form.Group>
        {community && (
          <Form.Field width={12}>
            <Grid fluid className="mt-0 mb-0">
              <CommunityListItem community={community} />
              {otherCommunities.map((c) => (
                <CommunityListItem key={c.id} community={c} />
              ))}
            </Grid>
          </Form.Field>
        )}
        <Form.Field width={community ? 4 : 6} className="right-btn-column">
          {community && !selectionButtonShown ? (
            <p>{changeOnDetailPageMessage}</p>
          ) : (
            <>
              <AddEditCommunityButton
                community={community}
                changeSelectedCommunity={changeSelectedCommunity}
                focusAddButtonHandler={focusAddButtonHandler}
                setModalOpen={setModalOpen}
                modalOpen={modalOpen}
                selectionButtonDisabled={selectionButtonDisabled}
                permissionsPerField={permissionsPerField}
              />
              {community && (
                <RemoveCommunityButton
                  community={community}
                  changeSelectedCommunity={changeSelectedCommunity}
                  selectionButtonDisabled={selectionButtonDisabled}
                />
              )}
            </>
          )}
        </Form.Field>
        {!community && (
          <Form.Field width={11} className="communities-helptext-wrapper">
            <label htmlFor="community-selector" className="helptext">
              {selectionButtonShown
                ? i18next.t(
                    "Do you want to submit this deposit for publication by a collection?"
                  )
                : changeOnDetailPageMessage}
            </label>
          </Form.Field>
        )}
      </Form.Group>

      {!isInReview && <PublicationReviewWarning />}

      {isInReview && (
        <InReviewMessage communityTitle={community?.metadata?.title} />
      )}

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
    </>
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
  disableCommunitySelectionButton:
    state.deposit.editorState.ui.disableCommunitySelectionButton,
  showCommunitySelectionButton:
    state.deposit.editorState.ui.showCommunitySelectionButton,
  showCommunityHeader: state.deposit.editorState.ui.showCommunityHeader,
});

const mapDispatchToProps = (dispatch) => ({
  changeSelectedCommunity: (community) => dispatch(changeSelectedCommunity(community)),
});

export const CommunityField = connect(
  mapStateToProps,
  mapDispatchToProps
)(CommunityFieldComponent);
