/*
 * Based on a file in Invenio Communities
 * Copyright (C) 2024 CERN.
 *
 * Modifications for Knowledge Commons Works
 * Copyright (C) 2026 Mesh Research
 *
 * Invenio and Knowledge Commons Works are both free software; you
 * can redistribute and/or modify them under the terms of the MIT License;
 * see LICENSE file for more details.
 */

import { i18next } from "@translations/kcworks/i18next";
import { Formik, useFormikContext } from "formik";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import React, { Component } from "react";
import ReactDOM from "react-dom";
import {
  FieldLabel,
  RadioField,
  SelectField,
  TextField,
  withCancel,
  http,
} from "react-invenio-forms";
import { Button, Divider, Form, Grid, Header, Icon, Message } from "semantic-ui-react";
import { CommunityApi } from "@js/invenio_communities/api";
import { communityErrorSerializer } from "@js/invenio_communities/api/serializers";
import Overridable, { OverridableContext, overrideStore } from "react-overridable";
import { getAncestorCommunities } from "./CommunitiesCardGroup";

/**
 * Initial create-vs-link mode from `?mode=new|link`.
 *
 * @returns {boolean} True when linking an existing collection (`mode=link`).
 */
function getInitialHasCommunity() {
  const params = new URLSearchParams(window.location.search);
  return params.get("mode") === "link";
}

/**
 * IDs that must not be selectable as a new subcollection of `community`.
 *
 * Includes the community itself and every ancestor (avoids hierarchy cycles).
 * Prefers server-provided ancestor ids; falls back to walking `community.parent`.
 *
 * @param {object} community - Current (proposed parent) community.
 * @param {string[]} [ancestorIds] - Ancestor ids from the page (breadcrumb).
 * @returns {Set<string>} Excluded community ids.
 */
function getExcludedCommunityIds(community, ancestorIds = []) {
  const excluded = new Set(
    (ancestorIds || []).filter(Boolean).map((id) => String(id))
  );
  if (community?.id) {
    excluded.add(String(community.id));
  }
  getAncestorCommunities(community).forEach((ancestor) => {
    if (ancestor.id) {
      excluded.add(String(ancestor.id));
    }
  });
  return excluded;
}

const IdentifierField = ({ formConfig }) => {
  const { values } = useFormikContext();

  const helpText = (
    <>
      {i18next.t(
        "This is your collection's unique identifier. You will be able to access your collection through the URL:"
      )}
      <br />
      {`${formConfig.SITE_UI_URL}/collections/${values["metadata"]["slug"]}`}
    </>
  );

  return (
    <TextField
      required
      id="metadata.slug"
      label={
        <FieldLabel
          htmlFor="metadata.slug"
          icon="barcode"
          label={i18next.t("Identifier")}
        />
      }
      fieldPath="metadata.slug"
      helpText={helpText}
      fluid
      className="text-muted"
      onKeyDown={(e) => {
        e.key === "Enter" && e.preventDefault();
      }}
    />
  );
};

IdentifierField.propTypes = {
  formConfig: PropTypes.object.isRequired,
};

class CommunityCreateForm extends Component {
  state = {
    error: "",
    hasCommunity: getInitialHasCommunity(),
    communities: [],
    communitiesLoading: true,
  };

  componentDidMount() {
    const { community, ancestorIds } = this.props;
    const excludedIds = getExcludedCommunityIds(community, ancestorIds);
    // Only collections with no parent yet (re-parenting is a separate flow).
    // children.allow is allowed — KCWorks supports multi-level nesting.
    const query = encodeURIComponent("-_exists_:parent");
    withCancel(
      http
        .get(`/api/user/communities?sort=newest&size=100&q=${query}`)
        .then((response) => response.data)
        .then((data) => {
          this.setState({
            communitiesLoading: false,
            communities: (data?.hits?.hits || [])
              .filter((item) => !excludedIds.has(String(item.id)))
              // Client-side guard: same eligibility as the query (truthy `parent`
              // object is how list UIs detect an existing parent relationship).
              .filter((item) => !item.parent)
              .map((item) => ({
                text: item.metadata.title,
                value: item.id,
                key: item.id,
              })),
          });
        })
        .catch((error) => {
          console.error(error);
          this.setState({ communitiesLoading: false });
        })
    );
  }

  componentWillUnmount() {
    this.cancellableCreate && this.cancellableCreate.cancel();
  }

  setGlobalError = (errorMsg) => {
    this.setState({ error: errorMsg });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);
    const client = new CommunityApi();
    const { hasCommunity } = this.state;
    const { community } = this.props;
    let payload = {};
    if (hasCommunity) {
      payload = { community_id: values["metadata"]["community"] };
    } else {
      payload = {
        community: {
          title: values["metadata"]["title"],
          slug: values["metadata"]["slug"],
        },
      };
    }
    this.cancellableCreate = withCancel(
      client.createSubcommunity(community.id, payload)
    );

    try {
      const response = await this.cancellableCreate.promise;
      setSubmitting(false);
      const requestID = response.data.id;
      window.location.href = `/collections/${community.slug}/requests/${requestID}`;
    } catch (error) {
      if (error === "UNMOUNTED") return;

      const { errors, message } = communityErrorSerializer(error);

      if (message) {
        this.setGlobalError(
          "The form contains errors or missing fields. Please verify before submitting"
        );
      }

      if (errors) {
        errors.forEach(({ field, messages }) => {
          const fieldPath = field.startsWith("metadata")
            ? field
            : `metadata.${field.split(".").pop()}`;
          setFieldError(fieldPath, messages[0]);
        });
      }
    }
  };

  render() {
    const { formConfig, canCreateRestricted, community } = this.props;
    const { hasCommunity, communities, communitiesLoading, error } = this.state;

    return (
      <Overridable
        id="InvenioCommunities.CommunityCreateForm.layout"
        formConfig={formConfig}
        canCreateRestricted={canCreateRestricted}
        error={error}
        community={community}
        IdentifierField={IdentifierField}
      >
        <Formik
          initialValues={{
            access: {
              visibility: "public",
            },
            community: {
              slug: "",
              title: "",
            },
            metadata: {
              slug: "",
            },
          }}
          onSubmit={this.onSubmit}
        >
          {({ values, isSubmitting, handleSubmit }) => (
            <Form onSubmit={handleSubmit} className="communities-creation">
              <Message hidden={error === ""} negative className="flashed">
                <Grid container centered>
                  <Grid.Column mobile={16} tablet={12} computer={8} textAlign="left">
                    <strong>{error}</strong>
                  </Grid.Column>
                </Grid>
              </Message>
              <Grid container centered>
                <Grid.Row>
                  <Grid.Column mobile={16} tablet={12} computer={8} textAlign="center">
                    <Header as="h1" className="rel-mt-2">
                      {i18next.t("Subcollection request")}
                    </Header>
                    <Divider />
                  </Grid.Column>
                </Grid.Row>
                <Grid.Row textAlign="left">
                  <Grid.Column mobile={16} tablet={12} computer={8}>
                    <div className="field">
                      <Form.Field>
                        {i18next.t("Do you already have an existing collection?")}
                      </Form.Field>
                      <Form.Group>
                        <RadioField
                          label={i18next.t("Yes")}
                          checked={hasCommunity === true}
                          value={i18next.t("Yes")}
                          onChange={() => {
                            this.setState({ hasCommunity: true });
                          }}
                          fieldPath="metadata.hasCommunity"
                        />
                        <RadioField
                          label={i18next.t("No")}
                          checked={hasCommunity === false}
                          value={i18next.t("No")}
                          onChange={() => {
                            this.setState({ hasCommunity: false });
                          }}
                          fieldPath="metadata.hasCommunity"
                        />
                      </Form.Group>
                    </div>
                    {hasCommunity && (
                      <SelectField
                        label={
                          <FieldLabel
                            icon="user"
                            label={i18next.t("Collection")}
                            id="community-label"
                            class="block"
                          />
                        }
                        fieldPath="metadata.community"
                        options={communities}
                        placeholder={
                          communitiesLoading
                            ? i18next.t("Loading...")
                            : i18next.t("Select a collection")
                        }
                        required
                        disabled={communitiesLoading || _isEmpty(communities)}
                      />
                    )}
                    {!hasCommunity && (
                      <>
                        <TextField
                          required
                          id="metadata.title"
                          fluid
                          fieldPath="metadata.title"
                          onKeyDown={(e) => {
                            e.key === "Enter" && e.preventDefault();
                          }}
                          label={
                            <FieldLabel
                              htmlFor="metadata.title"
                              icon="book"
                              label={i18next.t("Collection name")}
                            />
                          }
                        />
                        <IdentifierField formConfig={formConfig} />
                      </>
                    )}
                    {canCreateRestricted && (
                      <>
                        <Header as="h3">{i18next.t("Collection visibility")}</Header>
                        {formConfig.access.visibility.map((item) => (
                          <React.Fragment key={item.value}>
                            <RadioField
                              key={item.value}
                              fieldPath="access.visibility"
                              label={item.text}
                              labelIcon={item.icon}
                              checked={_get(values, "access.visibility") === item.value}
                              value={item.value}
                              onChange={({ event, data, formikProps }) => {
                                formikProps.form.setFieldValue(
                                  "access.visibility",
                                  item.value
                                );
                              }}
                            />
                            <label className="helptext">{item.helpText}</label>
                          </React.Fragment>
                        ))}
                      </>
                    )}
                  </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                  <Grid.Column textAlign="center">
                    <Button
                      positive
                      icon
                      labelPosition="left"
                      loading={isSubmitting}
                      disabled={isSubmitting}
                      type="button"
                      onClick={(event) => handleSubmit(event)}
                    >
                      <Icon name="plus" />
                      {hasCommunity
                        ? i18next.t("Create request")
                        : i18next.t("Create collection")}
                    </Button>
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Form>
          )}
        </Formik>
      </Overridable>
    );
  }
}

CommunityCreateForm.propTypes = {
  formConfig: PropTypes.object.isRequired,
  canCreateRestricted: PropTypes.bool.isRequired,
  community: PropTypes.object.isRequired,
  ancestorIds: PropTypes.arrayOf(PropTypes.string),
};

CommunityCreateForm.defaultProps = {
  ancestorIds: [],
};

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const canCreateRestricted = JSON.parse(domContainer.dataset.canCreateRestricted);
const community = JSON.parse(domContainer.dataset.community);
const ancestorIds = JSON.parse(domContainer.dataset.ancestorIds || "[]");

const overriddenComponents = overrideStore.getAll();
ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CommunityCreateForm
      formConfig={formConfig}
      canCreateRestricted={canCreateRestricted}
      community={community}
      ancestorIds={ancestorIds}
    />
  </OverridableContext.Provider>,
  domContainer
);
export default CommunityCreateForm;
