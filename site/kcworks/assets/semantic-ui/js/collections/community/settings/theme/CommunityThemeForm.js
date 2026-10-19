/*
 * This file is part of Knowledge Commons Works.
 * Copyright (C) 2026 Mesh Research.
 */

import { CommunityApi } from "@js/invenio_communities/api";
import { communityErrorSerializer } from "@js/invenio_communities/api/serializers";
import { i18next } from "@translations/kcworks/i18next";
import { Formik } from "formik";
import _cloneDeep from "lodash/cloneDeep";
import _defaultsDeep from "lodash/defaultsDeep";
import _isEmpty from "lodash/isEmpty";
import _pickBy from "lodash/pickBy";
import React, { useState } from "react";
import { Button, Form, Grid, Header, Icon, Message } from "semantic-ui-react";
import PropTypes from "prop-types";
import { ColorField, InlineLabeledField, ToggleField } from "./ColorField";
import { communityThemeValidationSchema } from "./themeValidationSchema";

const OPTIONAL_STYLE_KEYS = [
  "secondaryColor",
  "tertiaryColor",
  "secondaryTextColor",
  "tertiaryTextColor",
];

const FONT_KEYS = ["family", "weight", "size"];

const FORM_STATUS_ID = "community-theme-form-status";

/**
 * Saved/dirty status text for the theme form.
 *
 * @param {object} props - Component props.
 * @param {boolean} props.isDirty - Whether the form has unsaved changes.
 * @param {boolean} props.isSaved - Whether the latest save succeeded.
 * @param {boolean} [props.hiddenFromReaders] - When true, hide from assistive tech (duplicate placement).
 * @returns {React.ReactElement} Status region markup.
 */
function ThemeFormStatus({ classnames, isDirty, isSaved, hiddenFromReaders = false }) {
  const content =
    isSaved && !isDirty
      ? "Saved changes will be visible after you refresh the page"
      : isDirty
        ? "Changes will be visible after you save and refresh the page"
        : null;

  return isSaved || isDirty ? (
    <div
      id={FORM_STATUS_ID}
      role="status"
      aria-live="polite"
      aria-hidden={hiddenFromReaders ? "true" : "false"}
      aria-atomic="true"
      className={`ui info label ${classnames}`}
    >
      {i18next.t(content)}
    </div>
  ) : null;
}

ThemeFormStatus.propTypes = {
  isDirty: PropTypes.bool.isRequired,
  isSaved: PropTypes.bool.isRequired,
  hiddenFromReaders: PropTypes.bool,
};

ThemeFormStatus.defaultProps = {
  hiddenFromReaders: false,
};

const COLOR_FIELDS = [
  {
    fieldPath: "theme.style.primaryColor",
    labelKey: "Primary color",
    descriptionKey: "Used for accents, buttons, and highlights.",
  },
  {
    fieldPath: "theme.style.primaryTextColor",
    labelKey: "Primary text color",
    descriptionKey: "Text color on primary-themed elements.",
  },
  {
    fieldPath: "theme.style.mainHeaderBackgroundColor",
    labelKey: "Header background color",
    descriptionKey: "Background tint for the collection header area.",
  },
  {
    fieldPath: "theme.style.secondaryColor",
    labelKey: "Secondary color",
    descriptionKey: "Optional. Used for secondary buttons and menu accents.",
  },
  {
    fieldPath: "theme.style.secondaryTextColor",
    labelKey: "Secondary text color",
  },
  {
    fieldPath: "theme.style.tertiaryColor",
    labelKey: "Tertiary color",
  },
  {
    fieldPath: "theme.style.tertiaryTextColor",
    labelKey: "Tertiary text color",
  },
];

/**
 * Remove empty optional theme fields before persisting.
 *
 * @param {object|undefined} theme - Raw Formik theme values.
 * @returns {object|undefined} Sanitized theme payload.
 */
export function sanitizeTheme(theme) {
  if (!theme) {
    return theme;
  }

  const style = { ...(theme.style || {}) };

  OPTIONAL_STYLE_KEYS.forEach((key) => {
    if (!style[key]) {
      delete style[key];
    }
  });

  const font = style.font || {};
  const cleanedFont = _pickBy(font, (value) => !_isEmpty(value));
  if (_isEmpty(cleanedFont)) {
    delete style.font;
  } else {
    style.font = cleanedFont;
  }

  return {
    enabled: Boolean(theme.enabled),
    style: {
      ...style,
      mainHeaderUseLogo: Boolean(style.mainHeaderUseLogo),
      mainHeaderUseGradient: Boolean(style.mainHeaderUseGradient),
    },
  };
}

function getInitialValues(community) {
  return _defaultsDeep(_cloneDeep(community), {
    theme: {
      enabled: true,
      style: {
        primaryColor: "",
        secondaryColor: "",
        tertiaryColor: "",
        primaryTextColor: "",
        secondaryTextColor: "",
        tertiaryTextColor: "",
        mainHeaderBackgroundColor: "",
        mainHeaderUseLogo: false,
        mainHeaderUseGradient: false,
        font: {
          family: "",
          weight: "",
          size: "",
        },
      },
    },
  });
}

function CommunityThemeForm({ community, defaultTheme }) {
  const [error, setError] = useState(undefined);
  const [isSaved, setIsSaved] = useState(false);

  const hasError = error !== undefined;

  const onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);
    setIsSaved(false);

    try {
      const client = new CommunityApi();
      const payload = {
        ...values,
        theme: sanitizeTheme(values.theme),
      };
      await client.update(community.id, payload);
      window.location.reload();
    } catch (submitError) {
      if (submitError === "UNMOUNTED") {
        return;
      }

      const { message, errors } = communityErrorSerializer(submitError);

      if (message) {
        setError(message);
      }

      if (errors) {
        errors.forEach(({ field, messages }) => setFieldError(field, messages[0]));
      }
    }

    setSubmitting(false);
  };

  const handleResetToDefaults = (resetForm) => {
    setIsSaved(false);
    setError(undefined);
    resetForm({
      values: {
        ...community,
        theme: _cloneDeep(defaultTheme),
      },
    });
  };

  return (
    <Formik
      initialValues={getInitialValues(community)}
      validationSchema={communityThemeValidationSchema}
      validateOnChange={false}
      validateOnBlur
      onSubmit={onSubmit}
    >
      {({ dirty: isDirty, handleSubmit, isSubmitting, resetForm }) => {
        const hasStatusMessage = isDirty || (isSaved && !isDirty);
        const statusDescribedBy = hasStatusMessage ? FORM_STATUS_ID : undefined;

        return (
          <Form onSubmit={handleSubmit} aria-describedby={statusDescribedBy}>
            <Message role="alert" hidden={!hasError} negative>
              <Message.Content>{error}</Message.Content>
            </Message>

            <Header as="h2" size="small">
              {i18next.t("Theme")}
              <Header.Subheader className="mt-5">
                {i18next.t("Customize colors and typography for this collection.")}
              </Header.Subheader>
              <Header.Subheader className="mt-5">
                {i18next.t(
                  "If you are using an auto-generated pattern for your logo, default colors are generated automatically based that image."
                )}
              </Header.Subheader>
            </Header>

            <ThemeFormStatus isDirty={isDirty} isSaved={isSaved} />

            {/* <ThemeEnabledField /> */}

            <fieldset className="ui segment invenio-fieldset community-theme-colors">
              <legend className="rel-mb-1">
                <Header as="h3">{i18next.t("Colors")}</Header>
              </legend>

              <Grid stackable className="relaxed">
                {COLOR_FIELDS.map(({ fieldPath, labelKey, descriptionKey }) => (
                  <Grid.Column
                    key={fieldPath}
                    widescreen={8}
                    largeScreen={8}
                    computer={8}
                    tablet={16}
                    mobile={16}
                  >
                    <ColorField
                      fieldPath={fieldPath}
                      label={i18next.t(labelKey)}
                      description={descriptionKey ? i18next.t(descriptionKey) : undefined}
                    />
                  </Grid.Column>
                ))}
              </Grid>
            </fieldset>

            <fieldset className="ui segment invenio-fieldset community-theme-header">
              <legend className="rel-mb-1">
                <Header as="h3">{i18next.t("Header")}</Header>
              </legend>

              <ToggleField
                fieldPath="theme.style.mainHeaderUseLogo"
                label={i18next.t("Use logo as header background")}
                description={i18next.t(
                  "When enabled, the collection logo is tiled behind the header area."
                )}
              />
              <ToggleField
                fieldPath="theme.style.mainHeaderUseGradient"
                label={i18next.t("Use gradient header background")}
                description={i18next.t("When disabled, the header uses a solid background color.")}
              />
            </fieldset>

            {/* FIXME: Add typography controls when supported

          <fieldset className="ui segment invenio-fieldset community-theme-typography">
            <legend className="rel-mb-1">
              <Header as="h3">{i18next.t("Typography")}</Header>
            </legend>

            <Form.Group unstackable>
              {FONT_KEYS.map((fontKey) => (
                <InlineLabeledField
                  key={fontKey}
                  fieldPath={`theme.style.font.${fontKey}`}
                  label={i18next.t(`Font ${fontKey}`)}
                />
              ))}
            </Form.Group>
          </fieldset>
          */}

            <Button
              primary
              icon
              labelPosition="left"
              loading={isSubmitting}
              toggle
              active={isSaved}
              type="submit"
              aria-describedby={statusDescribedBy}
            >
              <Icon name="save" />
              {isSaved ? i18next.t("Saved") : i18next.t("Save")}
            </Button>
            <Button
              type="button"
              icon
              labelPosition="left"
              disabled={!defaultTheme}
              onClick={() => handleResetToDefaults(resetForm)}
            >
              <Icon name="undo" />
              {i18next.t("Reset to defaults")}
            </Button>
            <br />
            <ThemeFormStatus
              classnames="rel-mt-1"
              isDirty={isDirty}
              isSaved={isSaved}
              hiddenFromReaders
            />
          </Form>
        );
      }}
    </Formik>
  );
}

CommunityThemeForm.propTypes = {
  community: PropTypes.object.isRequired,
  defaultTheme: PropTypes.object.isRequired,
};

export default CommunityThemeForm;
