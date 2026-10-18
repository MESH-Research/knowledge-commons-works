/**
 * Unit coverage for the webpack ``tinymce/tinymce`` → GPL shim alias target.
 */
describe("tinymceGplShim", () => {
  beforeEach(() => {
    jest.resetModules();
  });

  /**
   * @param {unknown} mod
   * @returns {object}
   */
  function unwrap(mod) {
    return mod && typeof mod === "object" && "default" in mod ? mod.default : mod;
  }

  it("sets license_key gpl and .min suffix via overrideDefaults", () => {
    const overrideDefaults = jest.fn();
    const on = jest.fn();
    jest.doMock("tinymce", () => ({
      __esModule: true,
      default: {
        overrideDefaults,
        on,
        defaultOptions: { branding: false },
      },
    }));

    // eslint-disable-next-line global-require
    const shimmed = unwrap(require("./tinymceGplShim"));

    expect(overrideDefaults).toHaveBeenCalledWith(
      expect.objectContaining({
        license_key: "gpl",
        branding: false,
        suffix: ".min",
      })
    );
    expect(on).toHaveBeenCalledWith("AddEditor", expect.any(Function));
    expect(shimmed.overrideDefaults).toBe(overrideDefaults);
  });

  it("falls back to defaultOptions when overrideDefaults is missing", () => {
    const on = jest.fn();
    jest.doMock("tinymce", () => ({
      __esModule: true,
      default: {
        on,
        defaultOptions: { menubar: false },
      },
    }));

    // eslint-disable-next-line global-require
    const shimmed = unwrap(require("./tinymceGplShim"));

    expect(shimmed.defaultOptions).toEqual(
      expect.objectContaining({
        license_key: "gpl",
        menubar: false,
        suffix: ".min",
      })
    );
    expect(shimmed.suffix).toBe(".min");
    expect(on).toHaveBeenCalledWith("AddEditor", expect.any(Function));
  });

  it("injects paragraph styles into the editor iframe on init", () => {
    const on = jest.fn();
    jest.doMock("tinymce", () => ({
      __esModule: true,
      default: {
        overrideDefaults: jest.fn(),
        on,
        defaultOptions: {},
      },
    }));

    // eslint-disable-next-line global-require
    require("./tinymceGplShim");

    const addEditorHandler = on.mock.calls.find(
      (call) => call[0] === "AddEditor"
    )[1];

    const styleNodes = [];
    const head = {
      appendChild: jest.fn((node) => {
        styleNodes.push(node);
      }),
    };
    const doc = {
      head,
      getElementById: jest.fn(() => null),
      createElement: jest.fn((tag) => {
        const el = { tagName: tag.toUpperCase(), id: "", textContent: "" };
        return el;
      }),
    };
    const editorOn = jest.fn();
    addEditorHandler({
      editor: {
        on: editorOn,
        getDoc: () => doc,
      },
    });

    const initHandler = editorOn.mock.calls.find((call) => call[0] === "init")[1];
    initHandler();

    expect(doc.createElement).toHaveBeenCalledWith("style");
    expect(styleNodes).toHaveLength(1);
    expect(styleNodes[0].id).toBe("kcworks-richeditor-p-style");
    expect(styleNodes[0].textContent).toBe(
      "p { font-size: 1rem; line-height: 1.25em; }"
    );
    expect(head.appendChild).toHaveBeenCalledWith(styleNodes[0]);
  });
});
