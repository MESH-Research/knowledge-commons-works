import React from "react";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Formik, useFormikContext } from "formik";
import { render } from "@testing-library/react";
import { EmbargoCheckboxField } from "./EmbargoCheckboxField";

const ValuesProbe = () => {
  const { values } = useFormikContext();
  return (
    <pre data-testid="formik-values">{JSON.stringify(values)}</pre>
  );
};

const renderEmbargoCheckbox = (initialValues, { disabled = false, checked } = {}) => {
  const embargoActive = initialValues.access?.embargo?.active ?? false;
  return render(
    <Formik initialValues={initialValues} onSubmit={() => {}}>
      <>
        <EmbargoCheckboxField
          fieldPath="access.embargo.active"
          disabled={disabled}
          label="Apply an embargo"
          checked={checked ?? !!embargoActive}
        />
        <ValuesProbe />
      </>
    </Formik>
  );
};

const readValues = () =>
  JSON.parse(screen.getByTestId("formik-values").textContent);

describe("EmbargoCheckboxField", () => {
  it("enables embargo and restricts public files", async () => {
    renderEmbargoCheckbox({
      access: {
        record: "public",
        files: "public",
        embargo: { active: false },
      },
      files: { enabled: true },
    });

    userEvent.click(screen.getByTestId("embargo-checkbox-component"));

    await waitFor(() => {
      const values = readValues();
      expect(values.access.embargo.active).toBe(true);
      expect(values.access.files).toBe("restricted");
    });
  });

  it("enables embargo without rewriting already-restricted files", async () => {
    renderEmbargoCheckbox({
      access: {
        record: "public",
        files: "restricted",
        embargo: { active: false },
      },
      files: { enabled: true },
    });

    userEvent.click(screen.getByTestId("embargo-checkbox-component"));

    await waitFor(() => {
      const values = readValues();
      expect(values.access.embargo.active).toBe(true);
      expect(values.access.files).toBe("restricted");
    });
  });

  it("clears embargo on disable and leaves files restricted", async () => {
    renderEmbargoCheckbox({
      access: {
        record: "public",
        files: "restricted",
        embargo: { active: true, until: "2030-01-01", reason: "hold" },
      },
      files: { enabled: true },
    });

    userEvent.click(screen.getByTestId("embargo-checkbox-component"));

    await waitFor(() => {
      const values = readValues();
      expect(values.access.embargo).toEqual({ active: false });
      expect(values.access.files).toBe("restricted");
    });
  });

  it("does not touch access.files when files are disabled", async () => {
    renderEmbargoCheckbox({
      access: {
        record: "public",
        files: "public",
        embargo: { active: false },
      },
      files: { enabled: false },
    });

    userEvent.click(screen.getByTestId("embargo-checkbox-component"));

    await waitFor(() => {
      const values = readValues();
      expect(values.access.embargo.active).toBe(true);
      expect(values.access.files).toBe("public");
    });
  });

  it("uses current form values after resetForm (localStorage restore)", async () => {
    let resetFormFn;
    const ResetHarness = () => {
      const { resetForm } = useFormikContext();
      resetFormFn = resetForm;
      return (
        <>
          <EmbargoCheckboxField
            fieldPath="access.embargo.active"
            disabled={false}
            label="Apply an embargo"
            checked={false}
          />
          <ValuesProbe />
        </>
      );
    };

    render(
      <Formik
        initialValues={{
          access: {
            record: "public",
            files: "restricted",
            embargo: { active: false },
          },
          files: { enabled: false },
        }}
        onSubmit={() => {}}
      >
        <ResetHarness />
      </Formik>
    );

    // Simulate accepting a localStorage snapshot with public files enabled.
    resetFormFn({
      values: {
        access: {
          record: "public",
          files: "public",
          embargo: { active: false },
        },
        files: { enabled: true },
      },
    });

    await waitFor(() => {
      expect(readValues().access.files).toBe("public");
    });

    userEvent.click(screen.getByTestId("embargo-checkbox-component"));

    await waitFor(() => {
      const values = readValues();
      expect(values.access.embargo.active).toBe(true);
      expect(values.access.files).toBe("restricted");
    });
  });
});
