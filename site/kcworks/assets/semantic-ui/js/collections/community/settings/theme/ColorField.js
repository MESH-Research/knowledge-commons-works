/*
 * This file is part of Knowledge Commons Works.
 * Copyright (C) 2026 Mesh Research.
 */

import { i18next } from "@translations/kcworks/i18next";
import { useField } from "formik";
import React from "react";
import { Form, Button, Icon, Input } from "semantic-ui-react";
import PropTypes from "prop-types";

const HEX_COLOR_PATTERN = /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/;

/**
 * Normalize a value for use with `<input type="color">`.
 *
 * @param {string|undefined|null} value - Hex color string.
 * @returns {string} A valid 7-char hex color.
 */
function toColorInputValue(value) {
  if (typeof value === "string" && HEX_COLOR_PATTERN.test(value)) {
    if (value.length === 4) {
      const [, r, g, b] = value;
      return `#${r}${r}${g}${g}${b}${b}`;
    }
    return value;
  }
  return "#000000";
}

/**
 * Whether the field has a user-set color value.
 *
 * @param {string|undefined|null} value - Hex color string.
 * @returns {boolean} True when a non-empty value is present.
 */
function hasColorValue(value) {
  return typeof value === "string" && value.trim() !== "";
}

/**
 * Hex text field with a clear button (standard SUI action input).
 *
 * @param {object} props - Component props.
 * @param {string} props.id - Input element id.
 * @param {string} props.name - Formik field name.
 * @param {string} props.value - Current value.
 * @param {string} props.ariaLabel - Accessible name for the input.
 * @param {string} [props.placeholder] - Input placeholder.
 * @param {Function} props.onChange - Called with the new string value.
 * @param {Function} props.onBlur - Input blur handler.
 * @param {Function} props.onClear - Clears the field value.
 * @returns {React.ReactElement} Input and clear control.
 */
function ClearableTextInput({
  id,
  name,
  value,
  ariaLabel,
  placeholder,
  onBlur,
  onChange,
  onClear,
}) {
  return (
    <Input action fluid={false} className="w-rel-8">
      <input
        id={id}
        value={value || ""}
        name={name}
        onChange={(event) => onChange(event.target.value)}
        onBlur={onBlur}
        type="text"
        placeholder={placeholder}
        aria-label={ariaLabel}
      />
      <Button
        type="button"
        icon
        aria-label={i18next.t("Clear")}
        disabled={!value}
        onClick={onClear}
      >
        <Icon name="close" />
      </Button>
    </Input>
  );
}

ClearableTextInput.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  value: PropTypes.string,
  ariaLabel: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  onBlur: PropTypes.func.isRequired,
  onClear: PropTypes.func.isRequired,
};

ClearableTextInput.defaultProps = {
  value: "",
  placeholder: undefined,
};

/**
 * Color picker paired with a hex text field.
 *
 * @param {object} props - Component props.
 * @param {string} props.fieldPath - Formik field path.
 * @param {string} props.label - Field label.
 * @param {string} [props.description] - Optional help text.
 * @returns {React.ReactElement} Color field.
 */
export function ColorField({ fieldPath, label, description }) {
  const [field, meta, helpers] = useField(fieldPath);
  const hasError = meta.touched && Boolean(meta.error);
  const inputId = field.name.replace(/\./g, "-");
  const colorInputId = `${inputId}-color`;
  const hexInputId = `${inputId}-hex`;
  const hasValue = hasColorValue(field.value);
  const swatchColor = toColorInputValue(field.value);

  return (
    <Form.Field error={hasError}>
      <label htmlFor={hexInputId}>{label}</label>
      {description ? <div className="helptext">{description}</div> : null}
      <Input action labelPosition="left" fluid={false} className="theme-color-field">
        <label
          className={`ui label theme-color-swatch${hasValue ? "" : " theme-color-swatch-empty"}`}
          style={hasValue ? { backgroundColor: swatchColor } : undefined}
          aria-label={i18next.t("Pick color")}
        >
          <input
            id={colorInputId}
            type="color"
            className="theme-color-input-native"
            value={swatchColor}
            onChange={(event) => helpers.setValue(event.target.value)}
            onBlur={field.onBlur}
            tabIndex={-1}
            aria-hidden="true"
          />
        </label>
        <input
          id={hexInputId}
          type="text"
          name={field.name}
          value={field.value || ""}
          onChange={(event) => helpers.setValue(event.target.value)}
          onBlur={field.onBlur}
          placeholder="#RRGGBB"
          aria-label={label}
        />
        <Button
          type="button"
          icon
          aria-label={i18next.t("Clear")}
          disabled={!field.value}
          onClick={() => helpers.setValue("")}
        >
          <Icon name="close" />
        </Button>
      </Input>
      {hasError ? <div className="ui pointing above prompt label">{meta.error}</div> : null}
    </Form.Field>
  );
}

ColorField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  description: PropTypes.string,
};

ColorField.defaultProps = {
  description: undefined,
};

/**
 * Text field with a clear button, label above the control.
 *
 * @param {object} props - Component props.
 * @param {string} props.fieldPath - Formik field path.
 * @param {string} props.label - Field label.
 * @returns {React.ReactElement} Labeled text field.
 */
export function InlineLabeledField({ fieldPath, label }) {
  const [field, meta, helpers] = useField(fieldPath);
  const hasError = meta.touched && Boolean(meta.error);
  const inputId = field.name.replace(/\./g, "-");

  return (
    <Form.Field error={hasError}>
      <label htmlFor={inputId}>{label}</label>
      <ClearableTextInput
        id={inputId}
        name={field.name}
        value={field.value}
        ariaLabel={label}
        onChange={(value) => helpers.setValue(value)}
        onBlur={field.onBlur}
        onClear={() => helpers.setValue("")}
      />
      {hasError ? <div className="ui pointing above prompt label">{meta.error}</div> : null}
    </Form.Field>
  );
}

InlineLabeledField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
};

/**
 * Formik-bound toggle field.
 *
 * @param {object} props - Component props.
 * @param {string} props.fieldPath - Formik field path.
 * @param {string} props.label - Checkbox label.
 * @param {string} [props.description] - Optional help text.
 * @returns {React.ReactElement} Toggle field.
 */
export function ToggleField({ fieldPath, label, description }) {
  const [field, , helpers] = useField({ name: fieldPath, type: "checkbox" });

  return (
    <Form.Field>
      <Form.Checkbox
        toggle
        label={label}
        checked={Boolean(field.value)}
        onChange={(_event, { checked }) => helpers.setValue(checked)}
      />
      {description ? <div className="helptext">{description}</div> : null}
    </Form.Field>
  );
}

ToggleField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  description: PropTypes.string,
};

ToggleField.defaultProps = {
  description: undefined,
};

/**
 * Toggle for `theme.enabled`.
 *
 * @returns {React.ReactElement} Enabled checkbox field.
 */
export function ThemeEnabledField() {
  const [field, , helpers] = useField({ name: "theme.enabled", type: "checkbox" });

  return (
    <Form.Field>
      <Form.Checkbox
        toggle
        label={i18next.t("Enable community theme")}
        checked={Boolean(field.value)}
        onChange={(_event, { checked }) => helpers.setValue(checked)}
      />
      <div className="helptext">
        {i18next.t(
          "When enabled, custom colors and fonts are applied across the collection pages."
        )}
      </div>
    </Form.Field>
  );
}
