/**
 * @jest-environment jsdom
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import GuidesForm from './guides-form';
import { sum } from './guides-form';

test('adds 1 to 2 to equal 3', () => {
    expect(sum(1, 2)).toBe(3);
});

test('renders the guides form', () => {
    render(<GuidesForm />);

    expect(screen.getByText(/Name/));
    // expect(screen.getByRole("heading")).toHaveTextContent(/Doggy Directory/);
    // expect(screen.getByRole("combobox")).toHaveDisplayValue("Select a breed");
    expect(screen.getByRole('button')).toHaveTextContent(/Submit/);
    // expect(screen.getByRole("img")).toBeInTheDocument();
});