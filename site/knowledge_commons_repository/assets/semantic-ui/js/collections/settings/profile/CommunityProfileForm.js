/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2023 CERN.
 * Copyright (C) 2021-2022 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { Formik } from "formik";
import _cloneDeep from "lodash/cloneDeep";
import _defaultsDeep from "lodash/defaultsDeep";
import _get from "lodash/get";
import _isArray from "lodash/isArray";
import _isBoolean from "lodash/isBoolean";
import _isEmpty from "lodash/isEmpty";
import _isNull from "lodash/isNull";
import _isNumber from "lodash/isNumber";
import _isObject from "lodash/isObject";
import _map from "lodash/map";
import _mapValues from "lodash/mapValues";
import _pick from "lodash/pick";
import _pickBy from "lodash/pickBy";
import _unset from "lodash/unset";
import React, { Component } from "react";
import { FundingField } from "@js/invenio_vocabularies";
import {
  AccordionField,
  CustomFields,
  FieldLabel,
  RemoteSelectField,
  SelectField,
  TextField,
  TextAreaField,
} from "react-invenio-forms";
import { Button, Form, Grid, Icon, Message, Divider } from "semantic-ui-react";
import * as Yup from "yup";
import { CommunityApi } from "../../api";
import { communityErrorSerializer } from "../../api/serializers";
import { CustomFieldSerializer } from "./CustomFieldSerializer";
import PropTypes from "prop-types";
import { default as DangerZone } from "./DangerZone";
import { default as LogoUploader } from "./LogoUploader";
import Overridable from "react-overridable";

const COMMUNITY_VALIDATION_SCHEMA = Yup.object({
  metadata: Yup.object({
    title: Yup.string().max(250, i18next.t("Maximum number of characters is 2000")),
    description: Yup.string().max(
      250,
      i18next.t("Maximum number of characters is 250")
    ),
    website: Yup.string().url(i18next.t("Must be a valid URL")),
    type: Yup.object().shape({
      id: Yup.string(),
    }),
  }),
});

/**
 * Remove empty fields from community
 * Copied from react-invenio-deposit
 * @method
 * @param {object} obj - potentially empty object
 * @returns {object} community - without empty fields
 */
const removeEmptyValues = (obj) => {
  if (_isArray(obj)) {
    let mappedValues = obj.map((value) => removeEmptyValues(value));
    return mappedValues.filter((value) => {
      if (_isBoolean(value) || _isNumber(value)) {
        return value;
      }
      return !_isEmpty(value);
    });
  } else if (_isObject(obj)) {
    let mappedValues = _mapValues(obj, (value) => removeEmptyValues(value));
    return _pickBy(mappedValues, (value) => {
      if (_isArray(value) || _isObject(value)) {
        return !_isEmpty(value);
      }
      return !_isNull(value);
    });
  }
  return _isNumber(obj) || _isBoolean(obj) || obj ? obj : null;
};

class CommunityProfileForm extends Component {
  state = {
    error: "",
  };
  knownOrganizations = {};

  getInitialValues = () => {
    const { community } = this.props;
    let initialValues = _defaultsDeep(community, {
      id: "",
      slug: "",
      metadata: {
        description: "",
        title: "",
        curation_policy: "",
        type: {},
        website: "",
        organizations: [],
        funding: [],
      },
      // TODO: should this come from the backend?
      access: {
        visibility: "public",
        member_policy: "open",
        record_policy: "open",
      },
    });

    // create a map with all organizations that are not custom (part of the
    // vocabulary), so that on form submission, newly custom organization input
    // by the user can be identified and correctly sent to the backend.
    const organizationsNames = initialValues.metadata.organizations.map((org) => {
      const isNonCustomOrganization = org.id;
      if (isNonCustomOrganization) {
        this.knownOrganizations[org.name] = org.id;
      }
      return org.name;
    });

    _unset(initialValues, "metadata.type.title");
    /**
     * Deserializes a funding record (e.g. funder or award)
     *
     * @param {object} fund
     *
     * @returns {object} an object containing the deserialized record
     */
    const deserializeFunding = (fund) => {
      const _deserialize = (value) => {
        const deserializedValue = _cloneDeep(value);

        if (value?.title_l10n) {
          deserializedValue.title = value.title_l10n;
        }

        if (value.identifiers) {
          const allowedIdentifiers = ["url"];

          allowedIdentifiers.forEach((identifier) => {
            let identifierValue = null;
            value.identifiers.forEach((v) => {
              if (v.scheme === identifier) {
                identifierValue = v.identifier;
              }
            });

            if (identifierValue) {
              deserializedValue[identifier] = identifierValue;
            }
          });

          delete deserializedValue["identifiers"];
        }
        return deserializedValue;
      };

      let deserializedValue = {};
      if (fund !== null) {
        deserializedValue = Array.isArray(fund)
          ? fund.map(_deserialize)
          : _deserialize(fund);
      }

      return deserializedValue;
    };

    const funding = initialValues.ui.funding?.map((fund) => {
      return {
        ...(fund.award && { award: deserializeFunding(fund.award) }),
        funder: deserializeFunding(fund.funder),
      };
    });
    const { customFields } = this.props;

    // Deserialize custom fields
    initialValues = new CustomFieldSerializer({
      fieldpath: "custom_fields",
      deserializedDefault: {},
      serializedDefault: {},
      vocabularyFields: customFields.vocabularies,
    }).deserialize(initialValues);

    return {
      ...initialValues,
      metadata: {
        ...initialValues.metadata,
        organizations: organizationsNames,
        funding,
      },
    };
  };

  /**
   * Serializes community values
   *
   * @param {object} values
   *
   * @returns
   */
  serializeValues = (values) => {
    /**
     * Serializes a funding record (e.g. funder or award)
     *
     * @param {object} fund
     *
     * @returns {object} an object containing the serialized record
     */
    const serializeFunding = (fund) => {
      const _serialize = (value) => {
        if (value.id) {
          return { id: value.id };
        }

        // Record is a custom record, without explicit 'id'
        let clonedValue = _cloneDeep(value);
        // allowed keys
        const allowedKeys = ["identifiers", "number", "title"];
        clonedValue = _pick(clonedValue, allowedKeys);

        if (value.title) {
          clonedValue.title = {
            en: value.title,
          };
        }

        if (value.url) {
          clonedValue.identifiers = [
            {
              identifier: value.url,
              scheme: "url",
            },
          ];
          delete clonedValue["url"];
        }

        return clonedValue;
      };

      let serializedValue = {};
      if (fund !== null) {
        serializedValue = Array.isArray(fund) ? fund.map(_serialize) : _serialize(fund);
      }
      return serializedValue;
    };

    let submittedCommunity = _cloneDeep(values);

    // Serialize organisations. If it is known and has an id, serialize a pair 'id/name'. Otherwise use 'name' only
    const organizations = submittedCommunity.metadata.organizations.map(
      (organization) => {
        const orgID = this.knownOrganizations[organization];
        return {
          ...(orgID && { id: orgID }),
          name: organization,
        };
      }
    );
    // Serialize each funding record, award being optional.
    const funding = submittedCommunity.metadata?.funding?.map((fund) => {
      return {
        ...(fund.award && { award: serializeFunding(fund.award) }),
        funder: serializeFunding(fund.funder),
      };
    });
    const { customFields } = this.props;
    // Serialize custom fields
    submittedCommunity = new CustomFieldSerializer({
      fieldpath: "custom_fields",
      deserializedDefault: {},
      serializedDefault: {},
      vocabularyFields: customFields.vocabularies,
    }).serialize(submittedCommunity);

    submittedCommunity = {
      ...submittedCommunity,
      metadata: { ...values.metadata, organizations, funding },
    };

    // Clean values
    submittedCommunity = removeEmptyValues(submittedCommunity);

    return submittedCommunity;
  };

  setGlobalError = (error) => {
    const { message } = communityErrorSerializer(error);
    this.setState({ error: message });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);
    const payload = this.serializeValues(values);
    const client = new CommunityApi();
    const { community } = this.props;

    try {
      await client.update(community.id, payload);
      window.location.reload();
    } catch (error) {
      if (error === "UNMOUNTED") return;

      const { message, errors } = communityErrorSerializer(error);

      setSubmitting(false);

      if (message) {
        this.setGlobalError(error);
      }
      if (errors) {
        errors.map(({ field, messages }) => setFieldError(field, messages[0]));
      }
    }
  };

  render() {
    const {
      types,
      customFields,
      community,
      hasLogo,
      defaultLogo,
      logoMaxSize,
      permissions,
    } = this.props;
    const { error } = this.state;
    return (
      <Formik
        initialValues={this.getInitialValues(community)}
        validationSchema={COMMUNITY_VALIDATION_SCHEMA}
        onSubmit={this.onSubmit}
      >
        {({ isSubmitting, isValid, handleSubmit }) => (
          <Form onSubmit={handleSubmit} className="communities-profile">
            <Message hidden={error === ""} negative>
              <Grid container>
                <Grid.Column width={15} textAlign="left">
                  <strong>{error}</strong>
                </Grid.Column>
              </Grid>
            </Message>
            <Grid>
              <Grid.Row>
                <Grid.Column
                  as="section"
                  mobile={16}
                  tablet={10}
                  computer={11}
                  className="rel-pb-2"
                >
                  <AccordionField
                    includesPaths={[
                      "metadata.title",
                      "metadata.type.id",
                      "metadata.website",
                      "metadata.organizations",
                      "metadata.description",
                    ]}
                    label={i18next.t("Basic information")}
                    active
                  >
                    <div className="rel-ml-1 rel-mr-1">
                      <TextField
                        fluid
                        fieldPath="metadata.title"
                        label={
                          <FieldLabel
                            htmlFor="metadata.title"
                            icon="book"
                            label={i18next.t("Name")}
                          />
                        }
                      />

                      <Overridable
                        id="InvenioCommunities.CommunityProfileForm.TextAreaField.MetadataDescription"
                        community={community}
                      >
                        <TextAreaField
                          fieldPath="metadata.description"
                          label={
                            <FieldLabel
                              htmlFor="metadata.description"
                              icon="pencil"
                              label={i18next.t("Short description")}
                            />
                          }
                          fluid
                        />
                      </Overridable>

                      <Overridable
                        id="InvenioCommunities.CommunityProfileForm.SelectField.MetadataType"
                        community={community}
                      >
                        <SelectField
                          search
                          clearable
                          fieldPath="metadata.type.id"
                          label={
                            <FieldLabel
                              htmlFor="metadata.type.id"
                              icon="tag"
                              label={i18next.t("Type")}
                            />
                          }
                          options={types.map((ct) => {
                            return {
                              value: ct.id,
                              text: ct?.title_l10n ?? ct.id,
                            };
                          })}
                        />
                      </Overridable>

                      <Overridable
                        id="InvenioCommunities.CommunityProfileForm.TextField.MetadataWebsite"
                        community={community}
                      >
                        <TextField
                          fieldPath="metadata.website"
                          label={
                            <FieldLabel
                              htmlFor="metadata.website"
                              icon="chain"
                              label={i18next.t("Website")}
                            />
                          }
                          fluid
                        />
                      </Overridable>

                      <Overridable
                        id="InvenioCommunities.CommunityProfileForm.RemoteSelectField.MetadataOrganizations"
                        community={community}
                      >
                        <RemoteSelectField
                          fieldPath="metadata.organizations"
                          suggestionAPIUrl="/api/affiliations"
                          suggestionAPIHeaders={{
                            Accept: "application/json",
                          }}
                          placeholder={i18next.t("Search for an organization by name")}
                          clearable
                          multiple
                          initialSuggestions={_get(
                            community,
                            "metadata.organizations",
                            []
                          )}
                          serializeSuggestions={(organizations) =>
                            _map(organizations, (organization) => {
                              // eslint-disable-next-line no-prototype-builtins
                              const isKnownOrg = this.knownOrganizations.hasOwnProperty(
                                organization.name
                              );
                              if (!isKnownOrg) {
                                this.knownOrganizations = {
                                  ...this.knownOrganizations,
                                  [organization.name]: organization.id,
                                };
                              }
                              return {
                                text: organization.name,
                                value: organization.name,
                                key: organization.name,
                              };
                            })
                          }
                          label={
                            <FieldLabel
                              htmlFor="metadata.organizations"
                              icon="group"
                              label={i18next.t("Organizations")}
                            />
                          }
                          noQueryMessage={i18next.t("Search for organizations...")}
                          allowAdditions
                          search={(filteredOptions, searchQuery) => filteredOptions}
                        />
                      </Overridable>
                    </div>
                  </AccordionField>

                  <Overridable
                    id="InvenioCommunities.CommunityProfileForm.AccordionField.MetadataFunding"
                    community={community}
                  >
                    <AccordionField
                      includesPaths={["metadata.funding"]}
                      label={i18next.t("Funding information")}
                      active
                    >
                      <div className="rel-ml-1 rel-mr-1">
                        <FundingField
                          fieldPath="metadata.funding"
                          searchConfig={{
                            searchApi: {
                              axios: {
                                headers: {
                                  Accept: "application/vnd.inveniordm.v1+json",
                                },
                                url: "/api/awards",
                                withCredentials: false,
                              },
                            },
                            initialQueryState: {
                              sortBy: "bestmatch",
                              sortOrder: "asc",
                              layout: "list",
                              page: 1,
                              size: 5,
                            },
                          }}
                          label={i18next.t("Awards")}
                          labelIcon="money bill alternate outline"
                          deserializeAward={(award) => {
                            return {
                              title: award.title_l10n,
                              pid: award.pid,
                              number: award.number,
                              funder: award.funder ?? "",
                              id: award.id,
                              ...(award.identifiers && {
                                identifiers: award.identifiers,
                              }),
                              ...(award.acronym && { acronym: award.acronym }),
                            };
                          }}
                          deserializeFunder={(funder) => {
                            return {
                              id: funder.id,
                              name: funder.name,
                              ...(funder.title_l10n && { title: funder.title_l10n }),
                              ...(funder.pid && { pid: funder.pid }),
                              ...(funder.country && { country: funder.country }),
                              ...(funder.identifiers && {
                                identifiers: funder.identifiers,
                              }),
                            };
                          }}
                          computeFundingContents={(funding) => {
                            let headerContent,
                              descriptionContent = "";
                            let awardOrFunder = "award";
                            if (funding.award) {
                              headerContent = funding.award.title;
                            }

                            if (funding.funder) {
                              const funderName =
                                funding.funder?.name ??
                                funding.funder?.title ??
                                funding.funder?.id ??
                                "";
                              descriptionContent = funderName;
                              if (!headerContent) {
                                awardOrFunder = "funder";
                                headerContent = funderName;
                                descriptionContent = "";
                              }
                            }

                            return {
                              headerContent,
                              descriptionContent,
                              awardOrFunder,
                            };
                          }}
                        />
                      </div>
                    </AccordionField>
                  </Overridable>

                  {!_isEmpty(customFields.ui) && (
                    <CustomFields
                      config={customFields.ui}
                      templateLoaders={[
                        (widget) => import(`@templates/custom_fields/${widget}.js`),
                        (widget) => import(`react-invenio-forms`),
                      ]}
                      fieldPathPrefix="custom_fields"
                    />
                  )}

                  <Divider hidden />
                  <Divider />
                  <Button
                    disabled={!isValid || isSubmitting}
                    loading={isSubmitting}
                    labelPosition="left"
                    primary
                    type="button"
                    icon
                    onClick={(event) => handleSubmit(event)}
                  >
                    <Icon name="save" />
                    {i18next.t("Save")}
                  </Button>
                </Grid.Column>
                <Grid.Column
                  as="section"
                  mobile={16}
                  tablet={5}
                  computer={4}
                  floated="right"
                >
                  <Overridable
                    id="InvenioCommunities.CommunityProfileForm.LogoUploader.ProfilePicture"
                    community={community}
                  >
                    <LogoUploader
                      community={community}
                      hasLogo={hasLogo}
                      defaultLogo={defaultLogo}
                      onError={this.setGlobalError}
                      logoMaxSize={logoMaxSize}
                    />
                  </Overridable>
                </Grid.Column>
              </Grid.Row>
              <Overridable
                id="InvenioCommunities.CommunityProfileForm.GridRow.DangerZone"
                community={community}
              >
                <Grid.Row className="danger-zone">
                  <Grid.Column as="section" width={16}>
                    <DangerZone
                      community={community}
                      onError={this.setGlobalError}
                      permissions={permissions}
                    />
                  </Grid.Column>
                </Grid.Row>
              </Overridable>
            </Grid>
          </Form>
        )}
      </Formik>
    );
  }
}

CommunityProfileForm.propTypes = {
  community: PropTypes.object.isRequired,
  defaultLogo: PropTypes.string.isRequired,
  hasLogo: PropTypes.bool.isRequired,
  logoMaxSize: PropTypes.number.isRequired,
  customFields: PropTypes.object.isRequired,
  types: PropTypes.array.isRequired,
  permissions: PropTypes.object.isRequired,
};

export default CommunityProfileForm;
