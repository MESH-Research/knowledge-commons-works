/*
 * This file is part of Knowledge Commons Works.
 * Copyright (C) 2026 Mesh Research.
 */

/** @typedef {(value: unknown) => boolean} ThemeInputValidator */

export const HEX_COLOR_PATTERN = /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/;

const FONT_FAMILY_PATTERN = /^[\w\s,'".-]+$/;
const FONT_SIZE_PATTERN = /^\d+(\.\d+)?(em|rem|px|%)$/;
const FONT_WEIGHT_NUMERIC_PATTERN = /^[1-9]00$/;
const FONT_WEIGHT_KEYWORDS = new Set(["normal", "bold", "bolder", "lighter"]);
const NO_CSS_BREAKOUT_PATTERN = /^[^;{}\\]*$/;

/**
 * @param {unknown} value
 * @returns {boolean}
 */
export function isOptionalHexColor(value) {
  if (value === undefined || value === null || value === "") {
    return true;
  }
  return typeof value === "string" && HEX_COLOR_PATTERN.test(value.trim());
}

/**
 * @param {unknown} value
 * @returns {boolean}
 */
export function isOptionalFontFamily(value) {
  if (value === undefined || value === null || value === "") {
    return true;
  }
  if (typeof value !== "string") {
    return false;
  }
  const trimmed = value.trim();
  return (
    trimmed.length <= 200 &&
    NO_CSS_BREAKOUT_PATTERN.test(trimmed) &&
    FONT_FAMILY_PATTERN.test(trimmed)
  );
}

/**
 * @param {unknown} value
 * @returns {boolean}
 */
export function isOptionalFontWeight(value) {
  if (value === undefined || value === null || value === "") {
    return true;
  }
  if (typeof value === "number") {
    return value >= 100 && value <= 900 && value % 100 === 0;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    return FONT_WEIGHT_KEYWORDS.has(trimmed) || FONT_WEIGHT_NUMERIC_PATTERN.test(trimmed);
  }
  return false;
}

/**
 * @param {unknown} value
 * @returns {boolean}
 */
export function isOptionalFontSize(value) {
  if (value === undefined || value === null || value === "") {
    return true;
  }
  if (typeof value !== "string") {
    return false;
  }
  const trimmed = value.trim();
  return trimmed.length <= 20 && FONT_SIZE_PATTERN.test(trimmed);
}

/**
 * @param {unknown} value
 * @returns {boolean}
 */
export function isOptionalBoolean(value) {
  return value === undefined || value === null || typeof value === "boolean";
}
