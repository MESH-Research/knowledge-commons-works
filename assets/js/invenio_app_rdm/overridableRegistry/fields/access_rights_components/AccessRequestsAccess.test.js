import React from "react";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { renderWithFormik, setupFormMocks } from "@custom-test-utils/formik_test_utils";
import { setupStore } from "@custom-test-utils/redux_store";
import { AccessRequestsAccess } from "./AccessRequestsAccess";

const mockPut = jest.fn();

jest.mock("react-invenio-forms", () => {
  const actual = jest.requireActual("react-invenio-forms");
  return {
    ...actual,
    http: {
      put: (...args) => mockPut(...args),
    },
    withCancel: (promise) => ({
      promise,
      cancel: jest.fn(),
    }),
  };
});

jest.mock("./ShareModal", () => ({
  ShareModal: ({ open, defaultTabKey }) =>
    open ? (
      <div data-testid="share-modal" data-default-tab={defaultTabKey} />
    ) : null,
}));

const baseSettings = {
  allow_user_requests: false,
  allow_guest_requests: false,
  accept_conditions_text: null,
  secret_link_expiration: 0,
};

const renderAccessRequests = ({
  access = { record: "public", files: "restricted" },
  metadataOnly = false,
  settings = baseSettings,
  accessLink = "/api/records/test-record/access",
  canManage = true,
  storeOverrides = {},
} = {}) => {
  const formMocks = setupFormMocks({
    access,
    files: { enabled: !metadataOnly },
    parent: { access: { settings } },
    links: accessLink ? { access: accessLink } : {},
  });

  const store = setupStore({
    deposit: {
      editorState: { selectedCommunity: null },
      record: {
        id: "test-record",
        links: accessLink ? { access: accessLink } : {},
        parent: { access: { settings } },
      },
      permissions: { can_manage: canManage },
      config: { groups_enabled: false },
    },
    files: {
      entries: metadataOnly ? {} : { "file-1": { name: "a.pdf", size: 1 } },
    },
    ...storeOverrides,
  });

  return renderWithFormik(
    <Provider store={store}>
      <AccessRequestsAccess access={access} metadataOnly={metadataOnly} />
    </Provider>,
    { initialValues: formMocks.values }
  );
};

describe("AccessRequestsAccess", () => {
  beforeEach(() => {
    mockPut.mockReset();
    mockPut.mockResolvedValue({
      data: {
        parent: {
          access: {
            settings: {
              ...baseSettings,
              allow_user_requests: true,
            },
          },
        },
      },
    });
  });

  it("hides controls when files are public", () => {
    renderAccessRequests({
      access: { record: "public", files: "public" },
    });
    expect(screen.queryByTestId("access-requests-toggle")).not.toBeInTheDocument();
  });

  it("hides controls when the record is restricted", () => {
    renderAccessRequests({
      access: { record: "restricted", files: "restricted" },
    });
    expect(screen.queryByTestId("access-requests-toggle")).not.toBeInTheDocument();
  });

  it("hides controls for metadata-only deposits", () => {
    renderAccessRequests({
      access: { record: "public", files: "restricted" },
      metadataOnly: true,
    });
    expect(screen.queryByTestId("access-requests-toggle")).not.toBeInTheDocument();
  });

  it("shows controls when metadata is public and files are restricted", () => {
    renderAccessRequests();
    expect(screen.getByTestId("access-requests-toggle")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /settings/i })).toBeInTheDocument();
  });

  it("enables user access requests via PUT on toggle on", async () => {
    renderAccessRequests();

    userEvent.click(screen.getByTestId("access-requests-toggle"));

    await waitFor(() => {
      expect(mockPut).toHaveBeenCalledWith(
        "/api/records/test-record/access",
        expect.objectContaining({
          allow_user_requests: true,
          allow_guest_requests: false,
        })
      );
    });
  });

  it("disables both allow flags via PUT on toggle off", async () => {
    mockPut.mockResolvedValue({
      data: {
        parent: {
          access: {
            settings: {
              ...baseSettings,
              allow_user_requests: false,
              allow_guest_requests: false,
            },
          },
        },
      },
    });

    renderAccessRequests({
      settings: {
        ...baseSettings,
        allow_user_requests: true,
        allow_guest_requests: true,
      },
    });

    userEvent.click(screen.getByTestId("access-requests-toggle"));

    await waitFor(() => {
      expect(mockPut).toHaveBeenCalledWith(
        "/api/records/test-record/access",
        expect.objectContaining({
          allow_user_requests: false,
          allow_guest_requests: false,
        })
      );
    });
  });

  it("opens the share modal on the Settings tab", () => {
    renderAccessRequests();

    userEvent.click(screen.getByRole("button", { name: /settings/i }));

    const modal = screen.getByTestId("share-modal");
    expect(modal).toBeInTheDocument();
    expect(modal).toHaveAttribute("data-default-tab", "accessRequests");
  });

  it("disables controls when access link is missing", () => {
    renderAccessRequests({ accessLink: null });

    expect(
      screen.getByRole("checkbox", { name: /allow access requests/i })
    ).toBeDisabled();
    expect(screen.getByRole("button", { name: /settings/i })).toBeDisabled();
  });

  it("shows an error when the access settings PUT fails", async () => {
    mockPut.mockRejectedValue({ message: "boom" });
    renderAccessRequests();

    userEvent.click(screen.getByTestId("access-requests-toggle"));

    await waitFor(() => {
      expect(screen.getByText("boom")).toBeInTheDocument();
    });
  });
});
