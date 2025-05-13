import React from 'react';
import { screen, waitFor, act, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { setupStore } from '@custom-test-utils/redux_store';
import { renderWithProviders } from '@custom-test-utils/redux_test_utils';
import { AdditionalTitlesField } from './AdditionalTitlesField';
import { FormUIStateContext } from '@js/invenio_modular_deposit_form/InnerDepositForm';
import { renderWithFormik, setupFormMocks } from '@custom-test-utils/formik_test_utils';
import axios from 'axios';
import { Provider } from 'react-redux';
import { useFormikContext } from 'formik';

// Mock axios for API calls
jest.mock('axios');

const typeOptions = {
  type: [
    {
        "text": "Alternative title",
        "value": "alternative-title"
    },
    {
        "text": "Primary title, html stripped",
        "value": "primary-stripped"
    },
    {
        "text": "Subtitle",
        "value": "subtitle"
    },
    {
        "text": "Translated title",
        "value": "translated-title"
    },
    {
        "text": "Other",
        "value": "other"
    }
]
}

const baseFormUIState = {
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
};

describe('AdditionalTitlesField', () => {
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
            additional_titles: [],
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
            additional_titles: recordOptions,
          },
        },
      },
    };

    const formMocks = setupFormMocks({
      metadata: {
        additional_titles: formOptions,
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
          <AdditionalTitlesField
            fieldPath="metadata.additional_titles"
            options={typeOptions}
            recordUI={store.getState().deposit.record.ui}
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

    // Check for the add buttons
    const addTranslatedButton = screen.getByText('Add translated title');
    const addAlternativeButton = screen.getByText('Add alternative title');
    expect(addTranslatedButton).toBeInTheDocument();
    expect(addAlternativeButton).toBeInTheDocument();

    // Check that no title fields are rendered initially
    expect(screen.queryByLabelText('Additional title')).not.toBeInTheDocument();
  });

  it("renders two additional titles correctly both with and without language value", () => {
    const formOptions = [
      {
        title: "Title 1",
        type: "translated-title",
        lang: "eng",
      },
      {
        title: "Title 2",
        type: "alternative-title",
      },
    ]
    const recordOptions = [...formOptions];
    renderComponent(recordOptions, formOptions);

    // Check that two title fields are rendered
    const translatedTitleField = screen.getByLabelText('Translated title');
    const alternativeTitleField = screen.getByLabelText('Alternative title');
    expect(translatedTitleField).toBeInTheDocument();
    expect(alternativeTitleField).toBeInTheDocument();
  });

  it('adds a new title when clicking add button and updates the title subfield', async () => {
    const { formikValues } = renderComponent();

    // Click add button for translated title
    const addButton = screen.getByText('Add translated title');
    userEvent.click(addButton);

    // Check that title field is rendered
    const titleInput = await screen.findByLabelText('Translated title');
    expect(titleInput).toBeInTheDocument();

    // Check that type dropdown is rendered
    const typeDropdown = screen.getByLabelText('Type');
    expect(typeDropdown).toBeInTheDocument();

    // Check that language selector is rendered
    const languageSelector = screen.getByRole('combobox');
    expect(languageSelector).toBeInTheDocument();

    // Type "My Translated Title" in the title input
    userEvent.type(titleInput, 'My Translated Title');

    // Wait for formik values to update
    await waitFor(() => {
      expect(formikValues.current.metadata.additional_titles).toHaveLength(1);
      expect(formikValues.current.metadata.additional_titles[0]).toEqual({
        title: 'My Translated Title',
        type: 'translated-title',
        lang: ''
      });
    });
  });

  it('removes a title when clicking remove button', async () => {
    const { formikValues } = renderComponent();

    // Add a title
    const addButton = screen.getByText('Add translated title');
    userEvent.click(addButton);

    // Check that title field is rendered
    const titleInput = await screen.findByLabelText('Translated title');
    expect(titleInput).toBeInTheDocument();

    // Click remove button
    const removeButton = screen.getByRole('button', { name: /remove/i });
    userEvent.click(removeButton);

    // Check that title field is removed
    await waitFor(() => {
      expect(screen.queryByLabelText('Translated title')).not.toBeInTheDocument();
      expect(formikValues.current.metadata.additional_titles).toHaveLength(0);
    });
  });

  it('handles language selection correctly', async () => {
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

    // Add a title
    const addButton = screen.getByText('Add translated title');
    userEvent.click(addButton);

    // Get the language selector
    const languageSelector = screen.getByRole('combobox');
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

    // Click the "English" option in the dropdown
    const englishOption = await screen.findByRole('option', { name: 'English' });
    userEvent.click(englishOption);

    // Verify the selection was made
    const languageSelectorWithin = within(languageSelector);
    const selectedLabel = languageSelectorWithin.getByRole("alert");
    expect(selectedLabel).toHaveTextContent('English');

    expect(englishOption).toHaveClass('selected');
    // Verify that the type dropdown is closed
    await waitFor(() => {
      expect(languageSelector).toHaveAttribute('aria-expanded', 'false');
      expect(formikValues.current.metadata.additional_titles).toHaveLength(1);
      expect(formikValues.current.metadata.additional_titles[0].lang).toEqual({
        id: 'eng',
        title_l10n: 'English'
      });
    });
  });

  it('handles type selection correctly', async () => {
    const { formikValues } = renderComponent();

    // Add a title
    const addButton = screen.getByText('Add translated title');
    userEvent.click(addButton);

    // Get the type dropdown
    const typeDropdown = screen.getByLabelText('Type');
    userEvent.click(typeDropdown);

    // Select "Alternative Title"
    const alternativeTitleOption = screen.getByRole('option', { name: 'Alternative title' });
    userEvent.click(alternativeTitleOption);

    // Verify the selection was made
    const typeDropdownWithin = within(typeDropdown);
    expect(typeDropdownWithin.getByRole('alert')).toHaveTextContent('Alternative title');
    // Verify that the label for the input field is "Alternative title"
    const titleInput = screen.getByLabelText('Alternative title');
    expect(titleInput).toBeInTheDocument();
    // Verify that the dropdown option is selected
    expect(alternativeTitleOption).toHaveClass('selected');
    // Verify that the type dropdown is closed
    await waitFor(() => {
      expect(typeDropdown).toHaveAttribute('aria-expanded', 'false');
      expect(formikValues.current.metadata.additional_titles).toHaveLength(1);
      expect(formikValues.current.metadata.additional_titles[0].type).toBe('alternative-title');
    });
  });
});