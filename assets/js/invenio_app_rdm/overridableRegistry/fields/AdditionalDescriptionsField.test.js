// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021      Graz University of Technology.
// Copyright (C) 2022      TU Wien.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from 'react';
import { screen, waitFor, act, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { setupStore } from '@custom-test-utils/redux_store';
import { renderWithProviders } from '@custom-test-utils/redux_test_utils';
import { AdditionalDescriptionsField } from './AdditionalDescriptionsField';
import { FormUIStateContext } from '@js/invenio_modular_deposit_form/InnerDepositForm';
import { renderWithFormik, setupFormMocks } from '@custom-test-utils/formik_test_utils';
import axios from 'axios';
import { Provider } from 'react-redux';
import { useFormikContext } from 'formik';

// Mock axios for API calls
jest.mock('axios');

const descriptionTypes = {
  type: [
    {
      "text": "Abstract",
      "value": "abstract"
    },
    {
      "text": "Methods",
      "value": "methods"
    },
    {
      "text": "Other",
      "value": "other"
    },
    {
      "text": "Primary description, html stripped",
      "value": "primary-stripped"
    },
    {
      "text": "Series information",
      "value": "series-information"
    },
    {
      "text": "Table of contents",
      "value": "table-of-contents"
    },
    {
      "text": "Technical info",
      "value": "technical-info"
    }
  ]
}

const uiConfig = {
  additional_descriptions: [
    {
      "description": "Test description",
      "type": {
        "id": "methods",
        "title_l10n": "Methods"
      }
    }
  ]
}

const editorConfig = {
  "removePlugins": [
    "Image",
    "ImageCaption",
    "ImageStyle",
    "ImageToolbar",
    "ImageUpload",
    "MediaEmbed",
    "Table",
    "TableToolbar",
    "TableProperties",
    "TableCellProperties"
  ]
}

describe('AdditionalDescriptionsField', () => {
  let store;

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();

    // Mock axios.get to return empty results
    axios.get.mockResolvedValue({
      data: {
        hits: {
          hits: []
        }
      }
    });

    store = setupStore({
      deposit: {
        record: {
          ui: {
            additional_descriptions: [],
          },
        },
      },
    });
  });

  const renderComponent = (recordOptions = [], formOptions = []) => {
    const formikValuesRef = { current: null };
    const TestComponent = () => {
      const { values } = useFormikContext();
      formikValuesRef.current = values;
      return null;
    };

    const preloadedState = {
      deposit: {
        record: {
          ui: {
            additional_descriptions: recordOptions,
          },
        },
      },
    };

    const formMocks = setupFormMocks({
      metadata: {
        additional_descriptions: formOptions,
      },
    });

    store = setupStore(preloadedState);

    const result = renderWithFormik(
      <Provider store={store}>
        <FormUIStateContext.Provider
          value={{
            vocabularies: {
              metadata: {
                languages: {
                  limit_to: [],
                },
              },
            },
            currentFieldMods: {
              defaultFieldValues: {},
              descriptionMods: {},
              helpTextMods: {},
              iconMods: {},
              labelMods: {},
              placeholderMods: {},
              priorityFieldValues: {},
              extraRequiredFields: {},
            },
          }}
        >
          <AdditionalDescriptionsField
            fieldPath="metadata.additional_descriptions"
            options={descriptionTypes}
            recordUI={store.getState().deposit.record.ui}
            editorConfig={editorConfig}
          />
          <TestComponent />
        </FormUIStateContext.Provider>
      </Provider>,
      {
        initialValues: formMocks.values,
      }
    );

    return { ...result, formikValues: formikValuesRef };
  };

  it('renders empty state correctly', () => {
    renderComponent();

    // Check for the add button
    const addButton = screen.getByText('Add another description');
    expect(addButton).toBeInTheDocument();

    // Check that no description fields are rendered initially
    expect(screen.queryByLabelText('Additional description')).not.toBeInTheDocument();
  });

  it('adds a new description when clicking add button and updates Formik values', async () => {
    const { formikValues } = renderComponent();

    // Click add button
    const addButton = screen.getByText('Add another description');
    userEvent.click(addButton);

    // Check that description field is rendered
    const descriptionInput = await screen.findByLabelText('Additional description');
    expect(descriptionInput).toBeInTheDocument();

    // Check that type dropdown is rendered
    const typeDropdown = screen.getByLabelText('Type of description');
    expect(typeDropdown).toBeInTheDocument();

    // Check that language selector is rendered
    const languageSelector = screen.getByLabelText('Language');
    expect(languageSelector).toBeInTheDocument();

    // Type description text
    userEvent.type(descriptionInput, 'My test description');

    // Open the dropdown and select description type
    userEvent.click(typeDropdown);

    // Wait for dropdown options to appear
    const methodsOption = await screen.findByRole('option', { name: 'Methods' });
    userEvent.click(methodsOption);

    // Wait for formik values to update
    await waitFor(() => {
      expect(formikValues.current.metadata.additional_descriptions).toHaveLength(1);
      expect(formikValues.current.metadata.additional_descriptions[0]).toEqual({
        description: 'My test description',
        type: 'methods',
        lang: ''
      });
    }, { timeout: 10000 });
  });

  it('removes a description when clicking remove button and updates Formik values', async () => {
    const { formikValues } = renderComponent();

    // Add a description
    const addButton = screen.getByText('Add another description');
    userEvent.click(addButton);

    // Check that description field is rendered
    const descriptionInput = await screen.findByLabelText('Additional description');
    expect(descriptionInput).toBeInTheDocument();

    // Click remove button (one mobile, one desktop)
    const removeButtons = screen.getAllByRole('button', { name: /remove/i });
    expect(removeButtons).toHaveLength(2);
    userEvent.click(removeButtons[0]);

    // Check that description field is removed and Formik values are updated
    await waitFor(() => {
      expect(screen.queryByLabelText('Additional description')).not.toBeInTheDocument();
      expect(formikValues.current.metadata.additional_descriptions).toHaveLength(0);
    });
  });

  it('handles language selection correctly and updates Formik values', async () => {
    // Mock the API response for searching "english"
    axios.get.mockResolvedValueOnce({
      data: {
        hits: {
          hits: [
            { id: 'eng', title_l10n: 'English' }
          ]
        }
      }
    });

    const { formikValues } = renderComponent();

    // Add a description
    const addButton = screen.getByText('Add another description');
    userEvent.click(addButton);

    // Get the language selector
    const languageSelector = await screen.findByLabelText('Language');
    expect(languageSelector).toBeInTheDocument();

    // Type "english" in the search field
    userEvent.type(languageSelector, 'english');

    // Wait for the API call to resolve and the dropdown to update
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        '/api/vocabularies/languages',
        expect.objectContaining({
          headers: {
            Accept: 'application/vnd.inveniordm.v1+json'
          },
          params: expect.objectContaining({
            suggest: 'english',
            size: 20
          })
        })
      );
    });

    // Select English from the dropdown
    const englishOption = await screen.findByRole('option', { name: 'English' });
    userEvent.click(englishOption);

    // Check that Formik values are updated with the selected language
    await waitFor(() => {
      expect(formikValues.current.metadata.additional_descriptions[0].lang).toEqual({
        id: 'eng',
        title_l10n: 'English'
      });
    });
  });

  it('handles type selection correctly', async () => {
    renderComponent();

    // Add a description
    const addButton = screen.getByText('Add another description');
    userEvent.click(addButton);

    // Get the type dropdown
    const typeDropdown = screen.getByLabelText('Type of description');
    userEvent.click(typeDropdown);

    // Select "Abstract"
    const abstractOption = await screen.findByRole('option', { name: 'Abstract' });
    userEvent.click(abstractOption);

    // Verify the selection was made
    const withinDropdown = within(typeDropdown);
    const selectedLabel = withinDropdown.getByRole("alert");
    expect(selectedLabel).toHaveTextContent('Abstract');

    expect(abstractOption).toHaveClass('selected');
    // Verify that the type dropdown is closed
    await waitFor(() => {
      expect(typeDropdown).toHaveAttribute('aria-expanded', 'false');
    });
  });

  it('handles description text input correctly', async () => {
    renderComponent();

    // Add a description
    const addButton = screen.getByText('Add another description');
    userEvent.click(addButton);

    // Get the description input
    const descriptionInput = await screen.findByLabelText('Additional description');

    // Type some text
    userEvent.type(descriptionInput, 'This is a test description');

    // Verify the text was entered
    await waitFor(() => {
      expect(descriptionInput).toHaveValue('This is a test description');
    });
  });
});