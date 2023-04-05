import { act } from "react-dom/test-utils";
import { render, unmountComponentAtNode } from "react-dom";
import React from "react";
import Formatter from "./Formatter";

let container;
const result = {
  updated: "2022-09-06T14:30:31.576504+00:00",
  metadata: {
    title: "test",
    float: -10.555,
    updated: "2022-09-06T14:30:31.576504+00:00",
    type: {
      id: "event",
      title: {
        de: "Event",
        en: "Event",
      },
      updated: "2022-09-06T14:30:31.576504+00:00",
    },
  },
};
beforeEach(() => {
  // setup a DOM element as a render target
  container = document.createElement("div");
  document.body.appendChild(container);
});

afterEach(() => {
  // cleanup on exiting
  unmountComponentAtNode(container);
  container.remove();
  container = null;
});

it("Can format correctly simple date string", () => {
  const property = "updated";
  const resourceSchema = {
    updated: {
      createOnly: false,
      readOnly: true,
      required: false,
      metadata: {},
      title: null,
      type: "date",
    },
  };

  act(() => {
    render(
      <Formatter result={result} resourceSchema={resourceSchema} property={property} />,
      container
    );
  });

  // check value is correct
  expect(
    container.querySelector('[data-testid="date-formatter"]').textContent
  ).toContain("Sep 6, 2022, 2:30 PM");
});

it("Can format correctly nested date string", () => {
  const property = "metadata.type.updated";
  const resourceSchema = {
    metadata: {
      createOnly: false,
      metadata: {},
      properties: {
        type: {
          createOnly: false,
          metadata: {},
          properties: {
            updated: {
              createOnly: false,
              metadata: {},
              readOnly: true,
              required: false,
              title: null,
              type: "date",
            },
          },
          readOnly: false,
          required: false,
          title: null,
          type: "vocabulary",
        },
      },
      readOnly: false,
      required: true,
      title: null,
      type: "object",
    },
  };

  act(() => {
    render(
      <Formatter result={result} resourceSchema={resourceSchema} property={property} />,
      container
    );
  });

  // check value is correct
  expect(container.textContent).toContain("Sep 6, 2022, 2:30 PM");
});

it("Can format correctly simple string", () => {
  const property = "metadata.title";
  const resourceSchema = {
    metadata: {
      createOnly: false,
      metadata: {},
      properties: {
        title: {
          createOnly: false,
          readOnly: true,
          required: false,
          title: null,
          type: "string",
        },
      },
      readOnly: false,
      required: true,
      title: null,
      type: "object",
    },
  };

  act(() => {
    render(
      <Formatter result={result} resourceSchema={resourceSchema} property={property} />,
      container
    );
  });

  // check value is correct
  expect(container.textContent).toContain("test");
});

it("Can format correctly a floated number", () => {
  const property = "metadata.float";
  const resourceSchema = {
    metadata: {
      createOnly: false,
      metadata: {},
      properties: {
        float: {
          createOnly: false,
          readOnly: true,
          metadata: {},
          required: false,
          title: null,
          type: "float",
        },
      },
      readOnly: false,
      required: true,
      title: null,
      type: "object",
    },
  };

  act(() => {
    render(
      <Formatter result={result} resourceSchema={resourceSchema} property={property} />,
      container
    );
  });

  // check value is correct
  expect(container.textContent).toContain("-10.555");
});
