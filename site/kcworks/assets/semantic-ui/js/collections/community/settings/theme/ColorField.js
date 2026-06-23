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
 * Text input with a clear button, for use inside a labeled field group.
 *
 * @param {object} props - Component props.
 * @param {string} props.id - Input element id.
 * @param {string} props.name - Formik field name.
 * @param {string} props.value - Current value.
 * @param {string} props.ariaLabel - Accessible name for the input.
 * @param {string} [props.placeholder] - Input placeholder.
 * @param {object} [props.inputStyle] - Optional inline styles for the input.
 * @param {Function} props.onChange - SUI Input change handler.
 * @param {Function} props.onBlur - Input blur handler.
 * @param {Function} props.onClear - Clears the field value.
 * @returns {React.ReactElement} Input and clear control.
 */
function ClearableTextInput({
  id,
  action,
  name,
  value,
  ariaLabel,
  placeholder,
  inputStyle,
  onChange,
  onBlur,
  onClear,
}) {
  return (
    <Form.Group unstackable inline>
      <Form.Field>
        <Input
          id={id}
          action={action}
          actionPosition="left"
          fluid={false}
          value={value || ""}
          onChange={onChange}
          onBlur={onBlur}
          name={name}
          placeholder={placeholder}
          aria-label={ariaLabel}
          style={inputStyle}
        />
      </Form.Field>
      <Form.Field>
        <Button
          type="button"
          icon
          className="close-btn no-label"
          aria-label={i18next.t("Clear")}
          disabled={!value}
          onClick={onClear}
        >
          <Icon name="close" />
        </Button>
      </Form.Field>
    </Form.Group>
  );
}

ClearableTextInput.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  value: PropTypes.string,
  ariaLabel: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  inputStyle: PropTypes.object,
  onChange: PropTypes.func.isRequired,
  onBlur: PropTypes.func.isRequired,
  onClear: PropTypes.func.isRequired,
};

ClearableTextInput.defaultProps = {
  value: "",
  placeholder: undefined,
  inputStyle: undefined,
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

  return (
    <Form.Field error={hasError}>
      <label htmlFor={hexInputId}>{label}</label>
      <Form.Group unstackable>
        {/*<Form.Field error={hasError}>
          <label htmlFor={colorInputId}>{i18next.t("Color")}</label>
        </Form.Field>*/}
        <Form.Field error={hasError}>
          <ClearableTextInput
            id={hexInputId}
            action={
              <input
                id={colorInputId}
                type="color"
                value={toColorInputValue(field.value)}
                onChange={(event) => helpers.setValue(event.target.value)}
                onBlur={field.onBlur}
                aria-label={i18next.t("Color")}
              />
            }
            className="ui input w-rel-8"
            name={field.name}
            value={field.value}
            ariaLabel={label}
            placeholder="#RRGGBB"
            onChange={(_event, { value }) => helpers.setValue(value)}
            onBlur={field.onBlur}
            onClear={() => helpers.setValue("")}
          />
          <label htmlFor={hexInputId}>{i18next.t("Hex")}</label>
        </Form.Field>
      </Form.Group>
      {description ? <div className="helptext">{description}</div> : null}
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
 * Inline text field with its label below the control.
 *
 * @param {object} props - Component props.
 * @param {string} props.fieldPath - Formik field path.
 * @param {string} props.label - Field label.
 * @returns {React.ReactElement} Inline text field.
 */
export function InlineLabeledField({ fieldPath, label }) {
  const [field, meta, helpers] = useField(fieldPath);
  const hasError = meta.touched && Boolean(meta.error);
  const inputId = field.name.replace(/\./g, "-");

  return (
    <Form.Field error={hasError}>
      <ClearableTextInput
        id={inputId}
        name={field.name}
        value={field.value}
        ariaLabel={label}
        onChange={(_event, { value }) => helpers.setValue(value)}
        onBlur={field.onBlur}
        onClear={() => helpers.setValue("")}
      />
      <label htmlFor={inputId}>{label}</label>
      {hasError ? <div className="ui pointing above prompt label">{meta.error}</div> : null}
    </Form.Field>
  );
}

InlineLabeledField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
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
