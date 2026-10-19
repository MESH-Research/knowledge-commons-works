/**
 * Smoke tests: real TinyMCE 8 inside the actual RichEditor mount parents we ship.
 *
 * Contexts (real config / props, not jsdom stand-ins):
 * 1. Deposit — ``DescriptionsField`` with KCWorks ``AbstractComponent`` editorConfig
 * 2. Community — ``CommunityPagesForm`` (default RichEditor init; no editorConfig)
 * 3. Invitations — ``InvitationsMembersModal`` (``inputValue={() => message}`` + onBlur)
 *
 * ``tinymce/tinymce`` → ``tinymceGplShim.js`` (jest mapper = webpack alias).
 * jsdom cannot load TinyMCE skin/CSS URLs, so init forces ``skin`` /
 * ``content_css`` false only; production toolbar/plugins stay.
 *
 * Note: deposit mounts ``DescriptionsField`` directly with the same props
 * ``AbstractComponent`` supplies — importing ``AbstractComponent`` pulls the
 * modular-deposit barrel (Uppy ESM) which root Jest does not transform.
 */
import React from "react";
import { act, fireEvent, screen, waitFor, render } from "@testing-library/react";
import tinymce from "tinymce";
import { renderWithFormik } from "@custom-test-utils/formik_test_utils";
import { DescriptionsField } from "@js/invenio_rdm_records/src/deposit/fields/DescriptionsField/DescriptionsField";
import { CommunityPagesForm } from "@js/invenio_communities/settings/pages/CommunityPagesForm";
import { InvitationsMembersModal } from "@js/invenio_communities/members/invitations/invitationsModal/InvitationsMembersModal";
import { InvitationsContext } from "@js/invenio_communities/api/invitations/InvitationsContextProvider";

/** Same editorConfig ``AbstractComponent`` passes in production. */
const DEPOSIT_EDITOR_CONFIG = {
  toolbar:
    "blocks | bold italic codesample blockquote table | bullist numlist | outdent indent | link | wordcount | undo redo | code | custom_preview",
  removePlugins: [
    "Image",
    "ImageCaption",
    "ImageStyle",
    "ImageToolbar",
    "ImageUpload",
    "MediaEmbed",
    "Table",
    "TableToolbar",
    "TableProperties",
    "TableCellProperties",
  ],
};

/** Default RichEditor toolbar fragment (no file-attach button). */
const DEFAULT_RICH_EDITOR_TOOLBAR_MARKERS = [
  "bold italic",
  "link image",
  "custom_preview",
];

jest.mock("@tinymce/tinymce-react", () => {
  const React = require("react");
  const actual = jest.requireActual("@tinymce/tinymce-react");
  const captured = { inits: [], editorProps: [] };

  function Editor(props) {
    captured.inits.push({ ...(props.init || {}) });
    captured.editorProps.push({
      id: props.id,
      initialValue: props.initialValue,
      value: props.value,
      disabled: props.disabled,
    });
    return React.createElement(actual.Editor, props);
  }

  return { ...actual, Editor, __captured: captured };
});

const { __captured: tinymceReactCaptured } = jest.requireMock(
  "@tinymce/tinymce-react"
);

jest.mock("react-invenio-forms", () => {
  const actual = jest.requireActual("react-invenio-forms");
  const emptyHits = { data: { hits: { hits: [] } } };
  const httpPut = jest.fn().mockResolvedValue({ data: {} });
  const httpGet = jest.fn().mockResolvedValue(emptyHits);
  return {
    ...actual,
    http: {
      ...actual.http,
      get: httpGet,
      put: httpPut,
      post: jest.fn().mockResolvedValue({ data: {} }),
    },
    __httpPut: httpPut,
    __httpGet: httpGet,
  };
});

const { __httpPut: httpPut, __httpGet: httpGet } = jest.requireMock(
  "react-invenio-forms"
);

jest.mock(
  "../../../../dependencies/invenio-communities/invenio_communities/assets/semantic-ui/js/invenio_communities/api",
  () => {
    const actual = jest.requireActual(
      "../../../../dependencies/invenio-communities/invenio_communities/assets/semantic-ui/js/invenio_communities/api"
    );
    return {
      ...actual,
      UsersApi: jest.fn().mockImplementation(() => ({
        suggestUsers: jest.fn().mockResolvedValue([]),
      })),
    };
  }
);

jest.mock(
  "../../../../dependencies/invenio-communities/invenio_communities/assets/semantic-ui/js/invenio_communities/api/serializers",
  () => ({
    communityErrorSerializer: () => ({}),
  })
);

jest.mock(
  "../../../../dependencies/invenio-communities/invenio_communities/assets/semantic-ui/js/invenio_communities/members/components/SearchWithRoleSelection",
  () => ({
    SearchWithRoleSelection: ({ messageComponent, message }) => (
      <div data-testid="search-with-role">
        <div data-testid="invite-message-state">{message ?? ""}</div>
        {messageComponent}
      </div>
    ),
  })
);

jest.mock(
  "../../../../dependencies/invenio-rdm-records/invenio_rdm_records/assets/semantic-ui/js/invenio_rdm_records/src/deposit/fields/LanguagesField",
  () => ({
    LanguagesField: () => null,
  })
);

jest.setTimeout(20000);

function tinymceRoot() {
  return (typeof window !== "undefined" && window.tinymce) || tinymce;
}

/**
 * Force ``skin: false`` / ``content_css: false`` for jsdom only.
 *
 * TinyMCE’s default skin and content CSS are loaded as URLs (CDN or
 * ``skins/`` under the package). jsdom does not fetch those assets, so a
 * normal skin init hangs or never finishes. Production webpack serves the
 * skin; we do **not** strip toolbar/plugins here — those stay context-real.
 */
function patchTinymceInitForJsdom() {
  const root = tinymceRoot();
  if (!root || root.__kcworksJsdomInitPatched) {
    return;
  }
  const originalInit = root.init.bind(root);
  root.init = (settings) =>
    originalInit({
      ...settings,
      skin: false,
      content_css: false,
    });
  root.__kcworksJsdomInitPatched = true;
}

/**
 * @returns {object[]}
 */
function listEditors() {
  const root = tinymceRoot();
  if (!root) {
    return [];
  }
  if (typeof root.get === "function") {
    const all = root.get();
    if (Array.isArray(all)) {
      return all.filter((entry) => entry && entry.initialized);
    }
    if (all && all.initialized) {
      return [all];
    }
  }
  if (root.activeEditor && root.activeEditor.initialized) {
    return [root.activeEditor];
  }
  return [];
}

/**
 * @param {number} minCount
 * @returns {Promise<object[]>}
 */
async function waitForEditors(minCount = 1) {
  return waitFor(
    () => {
      const list = listEditors();
      if (list.length < minCount) {
        throw new Error(
          `expected ≥${minCount} TinyMCE editors, found ${list.length}`
        );
      }
      return list;
    },
    { timeout: 15000 }
  );
}

/**
 * @param {object} editor
 */
function blurEditor(editor) {
  if (typeof editor.dispatch === "function") {
    editor.dispatch("blur");
  } else {
    editor.fire("blur");
  }
}

/**
 * Programmatic HTML replace + blur (same API parents use after edits).
 *
 * @param {object} editor
 * @param {string} html
 */
async function setContentAndBlur(editor, html) {
  await act(async () => {
    editor.setContent(html);
    blurEditor(editor);
  });
}

/**
 * Type into the live contenteditable body (closer to user input than setContent).
 *
 * @param {object} editor
 * @param {string} text Plain text to type after clearing the body
 */
async function typeIntoEditorAndBlur(editor, text) {
  await act(async () => {
    editor.focus();
    const body = editor.getBody();
    body.focus();
    body.innerHTML = "";
    // TinyMCE listens to input on the body; insert text then notify.
    body.appendChild(body.ownerDocument.createTextNode(text));
    body.dispatchEvent(
      new body.ownerDocument.defaultView.Event("input", { bubbles: true })
    );
    editor.nodeChanged();
    blurEditor(editor);
  });
}

/** @param {object[]} editors */
function expectGplLicense(editors) {
  editors.forEach((editor) => {
    expect(editor.options.get("license_key")).toBe("gpl");
  });
}

/**
 * @param {string} toolbar
 * @param {string[]} markers
 */
function expectToolbarContains(toolbar, markers) {
  const normalized = String(toolbar || "");
  markers.forEach((marker) => {
    expect(normalized).toContain(marker);
  });
}

/**
 * Visible text from a live editor (jsdom TinyMCE text serializer is unreliable).
 *
 * @param {object} editor
 * @returns {string}
 */
function editorPlainText(editor) {
  const body = editor.getBody && editor.getBody();
  if (body && typeof body.textContent === "string") {
    return body.textContent.replace(/\u00a0/g, " ").trim();
  }
  return String(editor.getContent() || "")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

beforeEach(() => {
  patchTinymceInitForJsdom();
  const root = tinymceRoot();
  if (root && typeof root.remove === "function") {
    root.remove();
  }
  tinymceReactCaptured.inits.length = 0;
  tinymceReactCaptured.editorProps.length = 0;
  httpPut.mockReset().mockResolvedValue({ data: {} });
  httpGet.mockReset().mockResolvedValue({ data: { hits: { hits: [] } } });
});

afterEach(() => {
  const root = tinymceRoot();
  if (root && typeof root.remove === "function") {
    root.remove();
  }
});

describe("deposit DescriptionsField (AbstractComponent editorConfig)", () => {
  it("passes KCWorks editorConfig and writes both description fields on blur", async () => {
    let latestValues;

    renderWithFormik(
      ({ values }) => {
        latestValues = values;
        return (
          <DescriptionsField
            fieldPath="metadata.description"
            label="Description"
            recordUI={{}}
            options={{
              type: [{ text: "Abstract", value: "abstract" }],
            }}
            editorConfig={DEPOSIT_EDITOR_CONFIG}
          />
        );
      },
      {
        initialValues: {
          metadata: {
            description: "<p>main seed</p>",
            additional_descriptions: [
              {
                description: "<p>extra seed</p>",
                type: "abstract",
                lang: "",
              },
            ],
          },
        },
      }
    );

    const editors = await waitForEditors(2);
    expectGplLicense(editors);

    // Init args from RichEditor ← AbstractComponent editorConfig.
    expect(tinymceReactCaptured.inits.length).toBeGreaterThanOrEqual(2);
    tinymceReactCaptured.inits.forEach((init) => {
      expect(init.toolbar).toBe(DEPOSIT_EDITOR_CONFIG.toolbar);
      expect(init.removePlugins).toEqual(DEPOSIT_EDITOR_CONFIG.removePlugins);
    });
    editors.forEach((editor) => {
      expect(editor.options.get("toolbar")).toBe(DEPOSIT_EDITOR_CONFIG.toolbar);
    });

    // Initial values: Formik initialValues → RichInputField initialValue/inputValue.
    const mainEditor = editors.find((e) => e.getContent().includes("main seed"));
    const additionalEditor = editors.find((e) =>
      e.getContent().includes("extra seed")
    );
    expect(mainEditor).toBeTruthy();
    expect(additionalEditor).toBeTruthy();
    expect(editorPlainText(mainEditor)).toBe("main seed");
    expect(editorPlainText(additionalEditor)).toBe("extra seed");
    expect(mainEditor.getContent()).toContain("main seed");
    expect(additionalEditor.getContent()).toContain("extra seed");

    // One typing update through the contenteditable body (not setContent).
    await typeIntoEditorAndBlur(mainEditor, "typed abstract");
    await setContentAndBlur(additionalEditor, "<p>extra updated</p>");

    await waitFor(() => {
      expect(latestValues.metadata.description).toContain("typed abstract");
      expect(
        latestValues.metadata.additional_descriptions[0].description
      ).toContain("extra updated");
    });
  });
});

describe("community CommunityPagesForm (curation policy + about page)", () => {
  it("uses default RichEditor init and submits Formik HTML", async () => {
    const originalLocation = window.location;
    const reload = jest.fn();
    delete window.location;
    window.location = { ...originalLocation, reload, href: "http://localhost/" };

    try {
      render(
        <CommunityPagesForm
          community={{
            id: "comm-1",
            metadata: {
              curation_policy: "<p>policy seed</p>",
              page: "<p>about seed</p>",
            },
          }}
        />
      );

      const editors = await waitForEditors(2);
      expectGplLicense(editors);

      expect(tinymceReactCaptured.inits.length).toBeGreaterThanOrEqual(2);
      tinymceReactCaptured.inits.forEach((init) => {
        expectToolbarContains(init.toolbar, DEFAULT_RICH_EDITOR_TOOLBAR_MARKERS);
        // CommunityPagesForm does not pass editorConfig / removePlugins.
        expect(init.removePlugins).toBeUndefined();
      });
      editors.forEach((editor) => {
        expectToolbarContains(
          editor.options.get("toolbar"),
          DEFAULT_RICH_EDITOR_TOOLBAR_MARKERS
        );
      });

      // Initial values: community.metadata → Formik initialValues → editors.
      const policyEditor = editors.find((e) =>
        e.getContent().includes("policy seed")
      );
      const pageEditor = editors.find((e) =>
        e.getContent().includes("about seed")
      );
      expect(policyEditor).toBeTruthy();
      expect(pageEditor).toBeTruthy();
      expect(editorPlainText(policyEditor)).toBe("policy seed");
      expect(editorPlainText(pageEditor)).toBe("about seed");
      expect(policyEditor.getContent()).toContain("policy seed");
      expect(pageEditor.getContent()).toContain("about seed");

      await setContentAndBlur(policyEditor, "<p>policy updated</p>");
      await setContentAndBlur(pageEditor, "<p>about updated</p>");

      const saveButton = screen.getByRole("button", { name: /save/i });
      expect(saveButton).not.toBeDisabled();

      await act(async () => {
        fireEvent.click(saveButton);
      });

      await waitFor(() => {
        expect(httpPut).toHaveBeenCalled();
      });

      const submitted = httpPut.mock.calls[0][1];
      expect(submitted.metadata.curation_policy).toContain("policy updated");
      expect(submitted.metadata.page).toContain("about updated");
    } finally {
      window.location = originalLocation;
    }
  });
});

describe("invitations InvitationsMembersModal (message RichEditor)", () => {
  it("passes invite inputValue/onBlur contract and keeps message HTML", async () => {
    render(
      <InvitationsContext.Provider
        value={{
          api: {
            createInvite: jest.fn(),
            addGroupToMembers: jest.fn(),
          },
        }}
      >
        <InvitationsMembersModal
          updateQueryState={jest.fn()}
          currentQueryState={{}}
          rolesCanInvite={{
            user: [{ key: "reader", title: "Reader" }],
            group: [],
          }}
          groupsEnabled={false}
          community={{
            slug: "test-comm",
            links: {
              invitations: "/api/communities/test-comm/invitations",
              members: "/api/communities/test-comm/members",
            },
          }}
        />
      </InvitationsContext.Provider>
    );

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /invite/i }));
    });

    await screen.findByTestId("search-with-role");

    const editors = await waitForEditors(1);
    expectGplLicense(editors);

    expect(tinymceReactCaptured.inits.length).toBeGreaterThanOrEqual(1);
    const inviteInit = tinymceReactCaptured.inits[0];
    expectToolbarContains(inviteInit.toolbar, DEFAULT_RICH_EDITOR_TOOLBAR_MARKERS);
    expect(inviteInit.removePlugins).toBeUndefined();

    // Production passes ``inputValue={() => message}`` → Editor ``value`` prop.
    // message starts undefined → empty editor (same as opening the modal in prod).
    const inviteProps = tinymceReactCaptured.editorProps[0];
    expect(typeof inviteProps.value).toBe("function");
    expect(editorPlainText(editors[0])).toBe("");

    await setContentAndBlur(editors[0], "<p>please join</p>");

    await waitFor(() => {
      expect(screen.getByTestId("invite-message-state").textContent).toContain(
        "please join"
      );
    });
  });
});
