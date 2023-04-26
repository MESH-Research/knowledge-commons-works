/**
 * @jest-environment jsdom
 */

import { render, screen } from '@testing-library/react';
const guidesform = require('./components/guides-form.js');

test('adds 1 to 2 to equal 3', () => {
    expect(guidesform.sum(1, 2)).toBe(3);
});

test('renders the guides form', () => {
    render(guidesform.GuidesForm);

    // expect(screen.getByRole("heading")).toHaveTextContent(/Doggy Directory/);
    // expect(screen.getByRole("combobox")).toHaveDisplayValue("Select a breed");
    expect(screen.getByRole('submit')).toHaveTextContent(/Submit/);
    // expect(screen.getByRole("img")).toBeInTheDocument();
});