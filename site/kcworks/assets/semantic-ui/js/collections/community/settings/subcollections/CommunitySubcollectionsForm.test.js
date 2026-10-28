/*
 * This file is part of Knowledge Commons Works.
 * Copyright (C) 2026 Mesh Research.
 */

import { CommunityApi } from "@js/invenio_communities/api";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import CommunitySubcollectionsForm from "./CommunitySubcollectionsForm";

jest.mock("@js/invenio_communities/api");

const mockUpdate = jest.fn();

const community = {
  id: "comm-uuid-1",
  slug: "parent-collection",
  children: { allow: false },
  metadata: { title: "Parent" },
};

describe("CommunitySubcollectionsForm", () => {
  let reloadSpy;

  beforeEach(() => {
    mockUpdate.mockReset();
    mockUpdate.mockResolvedValue({});
    CommunityApi.mockImplementation(() => ({
      update: mockUpdate,
    }));
    reloadSpy = jest.fn();
    Object.defineProperty(window, "location", {
      configurable: true,
      value: { ...window.location, reload: reloadSpy },
    });
  });

  it("PUTs children.allow=true via CommunityApi.update on toggle", async () => {
    render(<CommunitySubcollectionsForm community={community} />);

    // Semantic UI Checkbox does not associate label text as the accessible name.
    userEvent.click(screen.getByRole("checkbox"));

    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledTimes(1);
    });

    expect(mockUpdate).toHaveBeenCalledWith(
      "comm-uuid-1",
      expect.objectContaining({
        id: "comm-uuid-1",
        slug: "parent-collection",
        children: expect.objectContaining({ allow: true }),
      })
    );
    expect(reloadSpy).toHaveBeenCalled();
  });

  it("reverts the toggle and shows an error when update fails", async () => {
    mockUpdate.mockRejectedValue({
      response: { data: { message: "Not allowed" } },
    });

    render(<CommunitySubcollectionsForm community={community} />);

    const checkbox = screen.getByRole("checkbox");
    userEvent.click(checkbox);

    await waitFor(() => {
      expect(screen.getByText("Not allowed")).toBeInTheDocument();
    });

    expect(checkbox).not.toBeChecked();
    expect(reloadSpy).not.toHaveBeenCalled();
  });
});

