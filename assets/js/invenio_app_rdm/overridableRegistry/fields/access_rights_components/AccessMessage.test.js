import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { renderWithFormik, setupFormMocks } from "@custom-test-utils/formik_test_utils";
import { setupStore } from "@custom-test-utils/redux_store";
import { AccessMessage, canShowShareAccessLink } from "./AccessMessage";

jest.mock(
  "@js/invenio_modular_deposit_form/field_components/patched/rdm_fields/share_components/DepositShareModal",
  () => ({
    DepositShareModal: ({ open }) =>
      open ? <div data-testid="deposit-share-modal" /> : null,
  })
);

jest.mock(
  "@js/invenio_modular_deposit_form/field_components/patched/rdm_fields/share_components/depositShareRecord",
  () => ({
    buildRecordForModal: (values) => values ?? {},
    fillMissingFromRedux: (values) => values,
    mergeShareRecordIntoFormik: (values) => values,
  })
);

const renderMessage = ({
  access = { record: "restricted", files: "restricted" },
  metadataOnly = false,
  accessCommunity = "public",
  canManage = true,
  recordParent = { access: { settings: {} } },
  isDraft = true,
} = {}) => {
  const formMocks = setupFormMocks({
    access,
    files: { enabled: !metadataOnly },
    parent: recordParent ? { access: recordParent.access } : {},
    expanded: { parent: {} },
  });

  const store = setupStore({
    deposit: {
      editorState: { selectedCommunity: null },
      record: {
        id: "test-record",
        is_draft: isDraft,
        parent: recordParent,
        links: { self: "/api/records/test-record" },
        expanded: { parent: {} },
      },
      permissions: { can_manage: canManage },
      config: { groups_enabled: false },
    },
  });

  return renderWithFormik(
    <Provider store={store}>
      <AccessMessage
        access={access}
        metadataOnly={metadataOnly}
        accessCommunity={accessCommunity}
      />
    </Provider>,
    { initialValues: formMocks.values }
  );
};

describe("canShowShareAccessLink", () => {
  it("matches the Share button display gate", () => {
    expect(
      canShowShareAccessLink({ parent: {}, is_draft: true }, { can_manage: true })
    ).toBe(true);
    expect(
      canShowShareAccessLink({ parent: {}, is_draft: null }, { can_manage: false })
    ).toBe(true);
    expect(
      canShowShareAccessLink({ parent: {}, is_draft: true }, { can_manage: false })
    ).toBe(false);
    expect(
      canShowShareAccessLink({ is_draft: true }, { can_manage: true })
    ).toBe(false);
  });
});

describe("AccessMessage", () => {
  it("links users specified to the share modal when Share is available", () => {
    renderMessage();

    const link = screen.getByTestId("users-specified-share-link");
    expect(link).toHaveTextContent("users specified");
    expect(link).toHaveStyle({ textDecoration: "underline dotted" });

    userEvent.click(link);
    expect(screen.getByTestId("deposit-share-modal")).toBeInTheDocument();
  });

  it("uses the pre-save wording when Share is hidden", () => {
    renderMessage({ recordParent: null });

    expect(
      screen.queryByTestId("users-specified-share-link")
    ).not.toBeInTheDocument();
    expect(screen.getByTestId("access-message")).toHaveTextContent(
      "accessed by specified users once a draft has been saved"
    );
  });

  it("links users specified for restricted files messages", () => {
    renderMessage({
      access: { record: "public", files: "restricted" },
    });

    expect(screen.getByTestId("users-specified-share-link")).toBeInTheDocument();
  });
});
