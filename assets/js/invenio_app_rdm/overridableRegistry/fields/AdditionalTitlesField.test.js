import React from 'react';
import { screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { setupStore } from '@custom-test-utils/redux_store';
import { renderWithProviders } from '@custom-test-utils/redux_test_utils';
import { AdditionalTitlesField } from './AdditionalTitlesField';
import { FormUIStateContext } from '@js/invenio_modular_deposit_form/InnerDepositForm';
import { renderWithFormik, setupFormMocks } from '@custom-test-utils/formik_test_utils';
import axios from 'axios';
import { Provider } from 'react-redux';

// Mock axios for API calls
jest.mock('axios');

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

    return renderWithFormik(
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
            options={{
              title: {
                label: "Title",
                placeholder: "Enter title",
              },
              type: {
                label: "Type",
                placeholder: "Select type",
                options: [
                  { text: "Alternative Title", value: "alternative_title" },
                  { text: "Subtitle", value: "subtitle" },
                  { text: "Translated Title", value: "translated_title" },
                ],
              },
            }}
            recordUI={store.getState().deposit.record.ui}
          />
        </FormUIStateContext.Provider>
      </Provider>,
      {
        initialValues: formMocks.values,
      }
    );
  };

  it('renders empty state correctly', () => {
    renderComponent();

    // Check for the add buttons
    const addTranslatedButton = screen.getByText('Add translated title');
    const addAlternativeButton = screen.getByText('Add alternative title');
    expect(addTranslatedButton).toBeInTheDocument();
    expect(addAlternativeButton).toBeInTheDocument();

    // Check that no title fields are rendered initially
    expect(screen.queryByPlaceholderText('Enter title')).not.toBeInTheDocument();
  });

  it('adds a new title when clicking add button', async () => {
    renderComponent();

    // Click add button for translated title
    const addButton = screen.getByText('Add translated title');
    await act(async () => {
      await userEvent.click(addButton);
    });

    // Check that title field is rendered
    const titleInput = await screen.findByPlaceholderText('Enter title');
    expect(titleInput).toBeInTheDocument();

    // Check that type dropdown is rendered
    const typeDropdown = screen.getByText('Select type');
    expect(typeDropdown).toBeInTheDocument();

    // Check that language selector is rendered
    const languageSelector = screen.getByText('Language');
    expect(languageSelector).toBeInTheDocument();
  });

  it('removes a title when clicking remove button', async () => {
    renderComponent();

    // Add a title
    const addButton = screen.getByText('Add other titles');
    await act(async () => {
      await userEvent.click(addButton);
    });

    // Check that title field is rendered
    const titleInput = await screen.findByPlaceholderText('Enter title');
    expect(titleInput).toBeInTheDocument();

    // Click remove button
    const removeButton = screen.getByRole('button', { name: /remove/i });
    await act(async () => {
      await userEvent.click(removeButton);
    });

    // Check that title field is removed
    await waitFor(() => {
      expect(screen.queryByPlaceholderText('Enter title')).not.toBeInTheDocument();
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

    renderComponent();

    // Add a title
    const addButton = screen.getByText('Add translated title');
    await userEvent.click(addButton);

    // Get the language selector
    const languageSelector = screen.getByRole('combobox');
    expect(languageSelector).toBeInTheDocument();

    // Type "english" in the search field
    await userEvent.type(languageSelector, 'english');

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
    const englishOption = await screen.findByText('English');
    await userEvent.click(englishOption);

    // Verify the selection was made
    const selectedLabel = screen.getByText('English').closest('a');
    expect(selectedLabel).toHaveClass('label');
    expect(selectedLabel).toHaveAttribute('value', 'eng');
  });

  it('handles type selection correctly', async () => {
    renderComponent();

    // Add a title
    const addButton = screen.getByText('Add translated title');
    await userEvent.click(addButton);

    // Get the type dropdown
    const typeDropdown = screen.getByText('Select type');
    await userEvent.click(typeDropdown);

    // Select "Alternative Title"
    const alternativeTitleOption = screen.getByText('Alternative Title');
    await userEvent.click(alternativeTitleOption);

    // Verify the selection was made
    expect(screen.getByText('Alternative Title')).toBeInTheDocument();
  });
});