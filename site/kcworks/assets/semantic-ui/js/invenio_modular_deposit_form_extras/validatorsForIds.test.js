import { addMethod } from "yup";
import * as yup from "yup";
import {
  gndValidator,
  isniValidator,
  kcUsernameValidator,
  orcidValidator,
  rorValidator,
} from "./validatorsForIds";

// Add validators to yup
addMethod(yup.string, "ror", rorValidator);
addMethod(yup.string, "isni", isniValidator);
addMethod(yup.string, "gnd", gndValidator);
addMethod(yup.string, "orcid", orcidValidator);
addMethod(yup.string, "kc_username", kcUsernameValidator);

describe("validatorsForIds", () => {
  describe("rorValidator", () => {
    const schema = yup.object().shape({
      ror: yup.string().nullable().ror(),
    });

    it("should validate correct ROR format", async () => {
      const validRORs = [
        "0w4pz9h89",
        "https://ror.org/0w4pz9h89",
        "http://ror.org/0w4pz9h89",
        "ror.org/0w4pz9h89",
      ];

      for (const ror of validRORs) {
        await expect(schema.validate({ ror })).resolves.toBeTruthy();
      }
    });

    it("should reject invalid ROR format", async () => {
      const invalidRORs = [
        "invalid",
        "12345678", // too short
        "0w4pz9h8", // too short
        "0w4pz9h890", // too long
        "https://example.com/0w4pz9h89", // wrong domain
        "https://ror.org/0w4pz9h8", // too short
        "https://ror.org/0w4pz9h890", // too long
      ];

      for (const ror of invalidRORs) {
        await expect(schema.validate({ ror }))
          .rejects.toThrow("Invalid ROR identifier");
      }
    });

    it("should handle null and undefined values", async () => {
      await expect(schema.validate({ ror: null }))
        .rejects.toThrow("ROR identifier cannot be empty");
      await expect(schema.validate({ ror: undefined }))
        .rejects.toThrow("ROR identifier cannot be empty");
      await expect(schema.validate({}))
        .rejects.toThrow("ROR identifier cannot be empty");
    });
  });

  describe("isniValidator", () => {
    const schema = yup.object().shape({
      isni: yup.string().isni(),
    });

    it("should validate correct ISNI format", async () => {
      const validISNIs = [
        "000000012146438X",
        "0000-0001-2146-438X",
        "0000 0001 2146 438X",
      ];

      for (const isni of validISNIs) {
        await expect(schema.validate({ isni })).resolves.toBeTruthy();
      }
    });

    it("should reject invalid ISNI format", async () => {
      const invalidISNIs = [
        "invalid",
        "1234567890123456",
        "0000000121464389",
      ];

      for (const isni of invalidISNIs) {
        await expect(schema.validate({ isni })).rejects.toThrow();
      }
    });

    it("should handle null and undefined values", async () => {
      await expect(schema.validate({ isni: null })).rejects.toThrow();
      await expect(schema.validate({ isni: undefined })).rejects.toThrow();
      await expect(schema.validate({})).rejects.toThrow();
    });
  });

  describe("gndValidator", () => {
    const schema = yup.object().shape({
      gnd: yup.string().nullable().gnd(),
    });

    it("should validate correct GND format", async () => {
      const validGNDs = [
        // Pattern 1: Start with 1 followed by optional 0, 1, or 2, then 7 digits and a check digit (X or number)
        "123456789", // starts with 1, 9 digits total
        "12345678X", // starts with 1, X check digit
        "100000000", // starts with 10, 10 digits total
        "101234567", // starts with 10, example with numbers
        "10123456X", // starts with 10, X check digit
        "111234567", // starts with 11, 10 digits total
        "1270543776", // starts with 12, 10 digits total (real-world example)

        // Pattern 2: Start with 4 or 7 followed by 6 digits and a hyphen and a digit
        "4000000-0",  // starts with 4
        "4123456-7",  // starts with 4, example with numbers
        "7000000-0",  // starts with 7
        "7123456-7",  // starts with 7, example with numbers

        // Pattern 3: Start with 1-9 followed by 0-7 digits and a hyphen and a check digit (X or number)
        "2-0",        // starts with 2, minimum length
        "21-7",       // starts with 2, 1 digit
        "212-7",      // starts with 2, 2 digits
        "2123-7",     // starts with 2, 3 digits
        "21234-7",    // starts with 2, 4 digits
        "212345-7",   // starts with 2, 5 digits
        "2123456-7",  // starts with 2, 6 digits
        "21234567-7", // starts with 2, 7 digits
        "21234567-X", // starts with 2, X check digit
        "5-0",        // starts with 5, minimum length
        "51-7",       // starts with 5, 1 digit
        "512-7",      // starts with 5, 2 digits
        "5123-7",     // starts with 5, 3 digits
        "51234-7",    // starts with 5, 4 digits
        "512345-7",   // starts with 5, 5 digits
        "5123456-7",  // starts with 5, 6 digits
        "51234567-7", // starts with 5, 7 digits
        "51234567-X", // starts with 5, X check digit

        // Pattern 4: Start with 3 followed by 7 digits and a check digit (X or number)
        "300000000", // starts with 3
        "312345678", // starts with 3, example with numbers
        "30000000X", // starts with 3, X check digit
        "31234567X", // starts with 3, example with numbers, X check digit

        // With prefixes
        "http://d-nb.info/gnd/100000000",
        "GND:100000000",
        "gnd:100000000",
      ];

      for (const gnd of validGNDs) {
        await expect(schema.validate({ gnd })).resolves.toBeTruthy();
      }
    });

    it("should reject invalid GND format", async () => {
      const invalidGNDs = [
        "invalid",                    // not a number
        "12345678",                  // missing hyphen/check digit
        "12345678-",                 // incomplete check digit
        "12345678-XX",               // invalid check digit format (two X's)
        "123456789-0",               // too many digits (8) before hyphen
        "0123456-7",                 // starts with 0 (not allowed)
        "4000000",                   // missing hyphen and check digit
        "https://example.com/100000000", // wrong domain
      ];

      for (const gnd of invalidGNDs) {
        await expect(schema.validate({ gnd }))
          .rejects.toThrow("Invalid GND");
      }
    });

    it("should handle null and undefined values", async () => {
      await expect(schema.validate({ gnd: null }))
        .rejects.toThrow("GND identifier cannot be empty");
      await expect(schema.validate({ gnd: undefined }))
        .rejects.toThrow("GND identifier cannot be empty");
      await expect(schema.validate({}))
        .rejects.toThrow("GND identifier cannot be empty");
    });
  });

  describe("orcidValidator", () => {
    const schema = yup.object().shape({
      orcid: yup.string().orcid(),
    });

    it("should validate correct ORCID format", async () => {
      const validORCIDs = [
        "0000-0001-2345-6789",
        "https://orcid.org/0000-0001-2345-6789",
        "http://orcid.org/0000-0001-2345-6789",
      ];

      for (const orcid of validORCIDs) {
        await expect(schema.validate({ orcid })).resolves.toBeTruthy();
      }
    });

    it("should reject invalid ORCID format", async () => {
      const invalidORCIDs = [
        "invalid",
        "1234-5678-9012-3456",
        "https://example.com/0000-0001-2345-6789",
      ];

      for (const orcid of invalidORCIDs) {
        await expect(schema.validate({ orcid })).rejects.toThrow();
      }
    });

    it("should handle null and undefined values", async () => {
      await expect(schema.validate({ orcid: null })).rejects.toThrow();
      await expect(schema.validate({ orcid: undefined })).rejects.toThrow();
      await expect(schema.validate({})).rejects.toThrow();
    });
  });

  describe("kcUsernameValidator", () => {
    const schema = yup.object().shape({
      kc_username: yup.string().nullable().kc_username(),
    });

    it("should validate correct Knowledge Commons username format", async () => {
      const validUsernames = [
        "john.doe",
        "jane_doe",
        "user123",
        "user@example.com",
        "user-name",
      ];

      for (const username of validUsernames) {
        await expect(schema.validate({ kc_username: username })).resolves.toBeTruthy();
      }
    });

    it("should reject usernames with invalid characters", async () => {
      const invalidUsernames = [
        "user name", // contains space
        "user@#$%", // contains special characters
        "<script>alert('xss')</script>", // contains HTML
        "user%20name", // contains percent encoding
        "user&nbsp;name", // contains HTML entity
        "user\u00E9", // contains accented character
        "user\u00A0", // contains non-breaking space
      ];

      for (const username of invalidUsernames) {
        await expect(schema.validate({ kc_username: username }))
          .rejects.toThrow("Username contains invalid characters");
      }
    });

    it("should reject usernames that are too short", async () => {
      const shortUsernames = [
        "", // empty string
        "a", // one character
        "ab", // two characters
      ];

      for (const username of shortUsernames) {
        await expect(schema.validate({ kc_username: username }))
          .rejects.toThrow("Username must be at least 3 characters long");
      }
    });

    it("should reject usernames with invalid format", async () => {
      const invalidUsernames = [
        "user name", // contains space
        "user@#$%", // contains special characters
      ];

      for (const username of invalidUsernames) {
        await expect(schema.validate({ kc_username: username }))
          .rejects.toThrow("Username contains invalid characters");
      }
    });

    it("should handle null and undefined values", async () => {
      await expect(schema.validate({ kc_username: null }))
        .rejects.toThrow("KC username cannot be empty");
      await expect(schema.validate({ kc_username: undefined }))
        .rejects.toThrow("KC username cannot be empty");
      await expect(schema.validate({}))
        .rejects.toThrow("KC username cannot be empty");
    });
  });
});