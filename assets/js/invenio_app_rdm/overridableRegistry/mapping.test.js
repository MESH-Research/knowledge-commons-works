/**
 * @jest-environment jsdom
 */

import { render, screen } from '@testing-library/react';
const overrides = require('./mapping.js');

test('renders the overridden metadata only toggle', () => {
    render(overrides.MetadataOnlyToggle);

    // expect(screen.getByRole("heading")).toHaveTextContent(/Doggy Directory/);
    // expect(screen.getByRole("combobox")).toHaveDisplayValue("Select a breed");
    // expect(screen.getByRole("button", { type: "submit" })).toHaveTextContent("Submit");
    // expect(screen.getByRole("img")).toBeInTheDocument();
});