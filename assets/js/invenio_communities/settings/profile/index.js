/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
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
import _pickBy from "lodash/pickBy";
import _unset from "lodash/unset";
import React, { Component } from "react";
import ReactDOM from "react-dom";
import Dropzone from "react-dropzone";
import { FundingField, humanReadableBytes } from "react-invenio-deposit";
import {
  CustomFields,
  FieldLabel,
  Image,
  RemoteSelectField,
  SelectField,
  TextField,
} from "react-invenio-forms";
import {
  Button,
  Divider,
  Form,
  Grid,
  Header,
  Icon,
  Message,
  Segment,
} from "semantic-ui-react";
import * as Yup from "yup";
import { CommunityApi } from "../../api";
import { communityErrorSerializer } from "../../api/serializers";
import { CustomFieldSerializer } from "./CustomFieldSerializer";
import { DeleteButton } from "./DeleteButton";
import { RenameCommunitySlugButton } from "./RenameCommunitySlugButton";
import PropTypes from "prop-types";

const COMMUNITY_VALIDATION_SCHEMA = Yup.object({
  metadata: Yup.object({
    title: Yup.string().max(250, i18next.t("Maximum number of characters is 2000")),
    description: Yup.string().max(
      2000,
      i18next.t("Maximum number of characters is 2000")
    ),
    website: Yup.string().url(i18next.t("Must be a valid URL")),
    type: Yup.object().shape({
      id: Yup.string(),
    }),
    // TODO: Re-enable once properly integrated to be displayed
    // page: Yup.string().max(2000, "Maximum number of characters is 2000"),
    // curation_policy: Yup.string().max(
    //   2000,
    //   "Maximum number of characters is 2000"
    // ),
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

const LogoUploader = ({ community, defaultLogo, hasLogo, onError, logoMaxSize }) => {
  const currentUrl = new URL(window.location.href);
  let dropzoneParams = {
    preventDropOnDocument: true,
    onDropAccepted: async (acceptedFiles) => {
      const file = acceptedFiles[0];
      const formData = new FormData();
      formData.append("file", file);

      try {
        const client = new CommunityApi();
        await client.updateLogo(community.id, file);
        // set param that logo was updated
        currentUrl.searchParams.set("updated", "true");

        window.location.replace(currentUrl.href);
      } catch (error) {
        onError(error);
      }
    },
    onDropRejected: (rejectedFiles) => {
      // TODO: show error message when files are rejected e.g size limit
      console.error(rejectedFiles[0].errors);
    },
    multiple: false,
    noClick: true,
    noDrag: true,
    noKeyboard: true,
    disabled: false,
    maxFiles: 1,
    maxSize: 5000000, // 5Mb limit
    accept: ".jpeg,.jpg,.png",
  };

  const deleteLogo = async () => {
    const client = new CommunityApi();
    await client.deleteLogo(community.id);
  };

  // when uploading a new logo, the previously cached logo will be displayed instead of the new one. Avoid it by randomizing the URL.
  const logoURL = new URL(community.links.logo);
  const noCacheRandomValue = new Date().getMilliseconds() * 5;
  logoURL.searchParams.set("no-cache", noCacheRandomValue.toString());

  const logoWasUpdated = currentUrl.searchParams.has("updated");

  return (
    <Dropzone {...dropzoneParams}>
      {({ getRootProps, getInputProps, open: openFileDialog }) => (
        <>
          <span {...getRootProps()}>
            <input {...getInputProps()} />
            <Header className="mt-0">{i18next.t("Profile picture")}</Header>
            <Image
              src={logoURL}
              fallbackSrc={defaultLogo}
              loadFallbackFirst
              fluid
              wrapped
              rounded
              className="community-logo settings"
            />

            <Divider hidden />
          </span>

          <Button
            fluid
            icon
            labelPosition="left"
            type="button"
            onClick={openFileDialog}
            className="rel-mt-1 rel-mb-1"
          >
            <Icon name="upload" />
            {i18next.t("Upload new picture")}
          </Button>
          <label className="helptext">
            {i18next.t("File must be smaller than ")}
            {humanReadableBytes(logoMaxSize, true)}
          </label>
          {hasLogo && (
            <DeleteButton
              label={i18next.t("Delete picture")}
              redirectURL={`${community.links.self_html}/settings?updated=true`}
              confirmationMessage={
                <Header as="h2" size="medium">
                  {i18next.t("Are you sure you want to delete this picture?")}
                </Header>
              }
              onDelete={deleteLogo}
              onError={onError}
            />
          )}
          {logoWasUpdated && (
            <Message
              info
              icon="warning circle"
              size="small"
              content={i18next.t(
                "It may take a few moments for changes to be visible everywhere"
              )}
            />
          )}
        </>
      )}
    </Dropzone>
  );
};

LogoUploader.propTypes = {
  community: PropTypes.object.isRequired,
  defaultLogo: PropTypes.string.isRequired,
  hasLogo: PropTypes.bool.isRequired,
  onError: PropTypes.func.isRequired,
  logoMaxSize: PropTypes.number.isRequired,
};

const DangerZone = ({ community, onError }) => (
  <Segment className="negative rel-mt-2">
    <Header as="h2" className="negative">
      {i18next.t("Danger zone")}
    </Header>
    <Grid>
      <Grid.Column mobile={16} tablet={10} computer={12}>
        <Header as="h3" size="small">
          {i18next.t("Change identifier")}
        </Header>
        <p>
          {i18next.t(
            "Changing your community's unique identifier can have unintended side effects."
          )}
        </p>
      </Grid.Column>
      <Grid.Column mobile={16} tablet={6} computer={4} floated="right">
        <RenameCommunitySlugButton community={community} />
      </Grid.Column>
      <Grid.Column mobile={16} tablet={10} computer={12} floated="left">
        <Header as="h3" size="small">
          {i18next.t("Delete community")}
        </Header>
        <p>{i18next.t("Once deleted, it will be gone forever. Please be certain.")}</p>
      </Grid.Column>
      <Grid.Column mobile={16} tablet={6} computer={4} floated="right">
        <DeleteButton
          community={community}
          label={i18next.t("Delete community")}
          redirectURL="/communities"
          confirmationMessage={
            <h3>{i18next.t("Are you sure you want to delete this community?")}</h3>
          }
          onDelete={async () => {
            const client = new CommunityApi();
            await client.delete(community.id);
          }}
          onError={onError}
        />
      </Grid.Column>
    </Grid>
  </Segment>
);

DangerZone.propTypes = {
  community: PropTypes.object.isRequired,
  onError: PropTypes.func.isRequired,
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
        // TODO: Re-enable once properly integrated to be displayed
        // curation_policy: "",
        // page: "",
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
        const clonedValue = _cloneDeep(value);
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
    const { types, customFields, community, hasLogo, defaultLogo, logoMaxSize } =
      this.props;
    const { error } = this.state;
    return (
      <Formik
        initialValues={this.getInitialValues(community)}
        validationSchema={COMMUNITY_VALIDATION_SCHEMA}
        onSubmit={this.onSubmit}
      >
        {({ isSubmitting, isValid, handleSubmit }) => (
          <Form onSubmit={handleSubmit} className="communities-profile">
            <Message hidden={error === ""} negative className="flashed">
              <Grid container>
                <Grid.Column width={15} textAlign="left">
                  <strong>{error}</strong>
                </Grid.Column>
              </Grid>
            </Message>
            <Grid>
              <Grid.Row className="pt-10 pb-0">
                <Grid.Column mobile={16} tablet={9} computer={9} className="rel-pb-2">
                  <TextField
                    fluid
                    fieldPath="metadata.title"
                    label={
                      <FieldLabel
                        htmlFor="metadata.title"
                        icon="book"
                        label={i18next.t("Community name")}
                      />
                    }
                  />
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
                  <TextField
                    fieldPath="metadata.description"
                    label={
                      <FieldLabel
                        htmlFor="metadata.description"
                        icon="pencil"
                        label={i18next.t("Description")}
                      />
                    }
                  />
                  <RemoteSelectField
                    fieldPath="metadata.organizations"
                    suggestionAPIUrl="/api/affiliations"
                    suggestionAPIHeaders={{
                      Accept: "application/json",
                    }}
                    placeholder={i18next.t("Search for an organization by name")}
                    clearable
                    multiple
                    initialSuggestions={_get(community, "metadata.organizations", [])}
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
                    label={i18next.t("Organizations")}
                    noQueryMessage={i18next.t("Search for organizations...")}
                    allowAdditions
                    search={(filteredOptions, searchQuery) => filteredOptions}
                  />
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
                    label="Awards"
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
                  {!_isEmpty(customFields.ui) && (
                    <CustomFields
                      config={customFields.ui}
                      templateLoader={(widget) =>
                        import(`@templates/custom_fields/${widget}.js`)
                      }
                      fieldPathPrefix="custom_fields"
                    />
                  )}

                  {/* TODO: Re-enable once properly integrated to be displayed */}
                  {/* <RichInputField
                    label="Curation policy"
                    fieldPath="metadata.curation_policy"
                    label={
                      <FieldLabel
                        htmlFor="metadata.curation_policy"
                        icon={"pencil"}
                        label="Curation policy"
                      />
                    }
                    editorConfig={CKEditorConfig}
                    fluid
                  />
                  <RichInputField
                    fieldPath="metadata.page"
                    label={
                      <FieldLabel
                        htmlFor="metadata.page"
                        icon={"pencil"}
                        label="Page description"
                      />
                    }
                    editorConfig={CKEditorConfig}
                    fluid
                  /> */}
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
                <Grid.Column mobile={16} tablet={6} computer={4} floated="right">
                  <LogoUploader
                    community={community}
                    hasLogo={hasLogo}
                    defaultLogo={defaultLogo}
                    onError={this.setGlobalError}
                    logoMaxSize={logoMaxSize}
                  />
                </Grid.Column>
              </Grid.Row>
              <Grid.Row className="danger-zone">
                <Grid.Column width={16}>
                  <DangerZone community={community} onError={this.setGlobalError} />
                </Grid.Column>
              </Grid.Row>
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
};

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);
const hasLogo = JSON.parse(domContainer.dataset.hasLogo);
const types = JSON.parse(domContainer.dataset.types);
const logoMaxSize = JSON.parse(domContainer.dataset.logoMaxSize);
const customFields = JSON.parse(domContainer.dataset.customFields);

ReactDOM.render(
  <CommunityProfileForm
    community={community}
    hasLogo={hasLogo}
    defaultLogo="/static/images/square-placeholder.png"
    types={types}
    logoMaxSize={logoMaxSize}
    customFields={customFields}
  />,
  domContainer
);
export default CommunityProfileForm;
