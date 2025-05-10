import React from 'react';
import { screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { setupStore } from '@custom-test-utils/redux_store';
import { renderWithProviders } from '@custom-test-utils/redux_test_utils';
import { AdditionalDescriptionsField } from './AdditionalDescriptionsField';
import { FormUIStateContext } from '@js/invenio_modular_deposit_form/InnerDepositForm';
import { renderWithFormik, setupFormMocks } from '@custom-test-utils/formik_test_utils';
import axios from 'axios';
import { Provider } from 'react-redux';

// Mock axios for API calls
jest.mock('axios');

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
          <AdditionalDescriptionsField
            fieldPath="metadata.additional_descriptions"
            options={{
              description: {
                label: "Description",
                placeholder: "Enter description",
              },
              type: {
                label: "Type",
                placeholder: "Select type",
                options: [
                  { text: "Abstract", value: "abstract" },
                  { text: "Methods", value: "methods" },
                  { text: "Technical Info", value: "technical_info" },
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

    // Check for the add button
    const addButton = screen.getByText('Add another description');
    expect(addButton).toBeInTheDocument();

    // Check that no description fields are rendered initially
    expect(screen.queryByPlaceholderText('Enter description')).not.toBeInTheDocument();
  });

  it('adds a new description when clicking add button', async () => {
    renderComponent();

    // Click add button
    const addButton = screen.getByText('Add another description');
    await act(async () => {
      await userEvent.click(addButton);
    });

    // Check that description field is rendered
    const descriptionInput = await screen.findByPlaceholderText('Enter description');
    expect(descriptionInput).toBeInTheDocument();

    // Check that type dropdown is rendered
    const typeDropdown = screen.getByText('Select type');
    expect(typeDropdown).toBeInTheDocument();

    // Check that language selector is rendered
    const languageSelector = screen.getByText('Language');
    expect(languageSelector).toBeInTheDocument();
  });

  it('removes a description when clicking remove button', async () => {
    renderComponent();

    // Add a description
    const addButton = screen.getByText('Add another description');
    await act(async () => {
      await userEvent.click(addButton);
    });

    // Check that description field is rendered
    const descriptionInput = await screen.findByPlaceholderText('Enter description');
    expect(descriptionInput).toBeInTheDocument();

    // Click remove button
    const removeButton = screen.getByRole('button', { name: /remove/i });
    await act(async () => {
      await userEvent.click(removeButton);
    });

    // Check that description field is removed
    await waitFor(() => {
      expect(screen.queryByPlaceholderText('Enter description')).not.toBeInTheDocument();
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

    // Add a description
    const addButton = screen.getByText('Add another description');
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

    // Add a description
    const addButton = screen.getByText('Add another description');
    await userEvent.click(addButton);

    // Get the type dropdown
    const typeDropdown = screen.getByText('Select type');
    await userEvent.click(typeDropdown);

    // Select "Abstract"
    const abstractOption = screen.getByText('Abstract');
    await userEvent.click(abstractOption);

    // Verify the selection was made
    expect(screen.getByText('Abstract')).toBeInTheDocument();
  });

  it('handles description text input correctly', async () => {
    renderComponent();

    // Add a description
    const addButton = screen.getByText('Add another description');
    await userEvent.click(addButton);

    // Get the description input
    const descriptionInput = screen.getByPlaceholderText('Enter description');

    // Type some text
    await userEvent.type(descriptionInput, 'This is a test description');

    // Verify the text was entered
    expect(descriptionInput).toHaveValue('This is a test description');
  });
});