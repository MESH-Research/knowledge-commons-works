import { addMethod } from "yup";
import * as yup from "yup";
import { kcUsernameValidator } from "./validatorsForIds";

addMethod(yup.string, "kc_username", kcUsernameValidator);

describe("validatorsForIds (KC extras)", () => {
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
        "user name",
        "user@#$%",
        "<script>alert('xss')</script>",
        "user%20name",
        "user&nbsp;name",
        "user\u00E9",
        "user\u00A0",
      ];

      for (const username of invalidUsernames) {
        await expect(schema.validate({ kc_username: username }))
          .rejects.toThrow("Username contains invalid characters");
      }
    });

    it("should reject usernames that are too short", async () => {
      const shortUsernames = ["", "a", "ab"];

      for (const username of shortUsernames) {
        await expect(schema.validate({ kc_username: username }))
          .rejects.toThrow("Username must be at least 3 characters long");
      }
    });

    it("should handle null and undefined values", async () => {
      await expect(schema.validate({ kc_username: null }))
        .rejects.toThrow("KC username cannot be empty");
      await expect(schema.validate({ kc_username: undefined }))
        .rejects.toThrow("KC username cannot be empty");
      await expect(schema.validate({})).rejects.toThrow("KC username cannot be empty");
    });
  });
});
