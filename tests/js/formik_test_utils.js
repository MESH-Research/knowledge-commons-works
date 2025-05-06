import React from 'react';
import { render } from '@testing-library/react';
import { Formik } from 'formik';

// Mock useFormikContext
export const mockSetFieldTouched = jest.fn();
export const mockSetFieldError = jest.fn();
export const mockSetFieldValue = jest.fn();
export const mockSetErrors = jest.fn();
export const mockSetTouched = jest.fn();
export const mockSetValues = jest.fn();
export const mockSetStatus = jest.fn();
export const mockSetSubmitting = jest.fn();
export const mockSetFormikState = jest.fn();
export const mockResetForm = jest.fn();
export const mockSubmitForm = jest.fn();
export const mockValidateForm = jest.fn();
export const mockValidateField = jest.fn();

export const mockFormikContext = {
  setFieldTouched: mockSetFieldTouched,
  setFieldError: mockSetFieldError,
  setFieldValue: mockSetFieldValue,
  setErrors: mockSetErrors,
  setTouched: mockSetTouched,
  setValues: mockSetValues,
  setStatus: mockSetStatus,
  setSubmitting: mockSetSubmitting,
  setFormikState: mockSetFormikState,
  resetForm: mockResetForm,
  submitForm: mockSubmitForm,
  validateForm: mockValidateForm,
  validateField: mockValidateField,
  values: {},
  errors: {},
  touched: {},
  isSubmitting: false,
  isValidating: false,
  dirty: false,
  isValid: false,
  initialValues: {},
  initialErrors: {},
  initialTouched: {},
  initialStatus: undefined,
};

// Helper function to render components with Formik context
export function renderWithFormik(
  ui,
  {
    initialValues = {},
    initialErrors = {},
    initialTouched = {},
    ...renderOptions
  } = {}
) {
  return render(
    <Formik
      initialValues={initialValues}
      initialErrors={initialErrors}
      initialTouched={initialTouched}
      onSubmit={() => {}}
    >
      {ui}
    </Formik>,
    renderOptions
  );
}

/**
 * Sets up basic form mocks with default values and mock functions.
 * Can be used for testing any form-related functionality.
 *
 * @param {Object} values - Optional values to override defaults
 * @returns {Object} Object containing form values and mock functions
 */
export function setupFormMocks(values = {}) {
  const defaultValues = {
    metadata: {
      identifiers: [],
      publisher: '',
    },
    files: {
      enabled: false,
    },
    ...values,
  };

  return {
    values: defaultValues,
    setFieldValue: mockSetFieldValue,
  };
}