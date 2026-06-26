import {
  HEX_COLOR_PATTERN,
  isOptionalBoolean,
  isOptionalFontFamily,
  isOptionalFontSize,
  isOptionalFontWeight,
  isOptionalHexColor,
} from "@js/kcworks/utils/themeInputValidation";

describe("themeInputValidation", () => {
  describe("isOptionalHexColor", () => {
    it("accepts empty values", () => {
      expect(isOptionalHexColor("")).toBe(true);
      expect(isOptionalHexColor(null)).toBe(true);
    });

    it("accepts #rgb and #rrggbb", () => {
      expect(isOptionalHexColor("#abc")).toBe(true);
      expect(isOptionalHexColor("#aabbcc")).toBe(true);
    });

    it("rejects invalid colors", () => {
      expect(isOptionalHexColor("red")).toBe(false);
      expect(isOptionalHexColor("#gggggg")).toBe(false);
      expect(isOptionalHexColor("#abc;")).toBe(false);
    });
  });

  describe("isOptionalFontWeight", () => {
    it("accepts keywords, numeric strings, and integers", () => {
      expect(isOptionalFontWeight("bold")).toBe(true);
      expect(isOptionalFontWeight("600")).toBe(true);
      expect(isOptionalFontWeight(600)).toBe(true);
    });

    it("rejects invalid weights", () => {
      expect(isOptionalFontWeight("650")).toBe(false);
      expect(isOptionalFontWeight("heavy")).toBe(false);
    });
  });

  describe("isOptionalFontSize", () => {
    it("accepts common CSS lengths", () => {
      expect(isOptionalFontSize("16px")).toBe(true);
      expect(isOptionalFontSize("1.25rem")).toBe(true);
    });

    it("rejects invalid sizes", () => {
      expect(isOptionalFontSize("large")).toBe(false);
    });
  });

  describe("isOptionalFontFamily", () => {
    it("accepts font stacks", () => {
      expect(isOptionalFontFamily("Arial, sans-serif")).toBe(true);
    });

    it("rejects CSS breakouts", () => {
      expect(isOptionalFontFamily("Arial;")).toBe(false);
    });
  });

  describe("isOptionalBoolean", () => {
    it("accepts booleans and empty values", () => {
      expect(isOptionalBoolean(true)).toBe(true);
      expect(isOptionalBoolean(false)).toBe(true);
      expect(isOptionalBoolean(undefined)).toBe(true);
    });

    it("rejects non-booleans", () => {
      expect(isOptionalBoolean("true")).toBe(false);
    });
  });

  it("exports HEX_COLOR_PATTERN for color inputs", () => {
    expect(HEX_COLOR_PATTERN.test("#fff")).toBe(true);
  });
});
