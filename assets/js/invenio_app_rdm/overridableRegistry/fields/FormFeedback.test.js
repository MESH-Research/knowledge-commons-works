import React from 'react';
import { render } from '@testing-library/react';
import { FormFeedback, ErrorMessageHandler } from './FormFeedback';
import { useFormikContext } from 'formik';

import { renderWithProviders } from '@custom-test-utils/redux_test_utils';
import { sampleState } from '@custom-test-utils/redux_store';
import { defaultFieldLabels } from './FormFeedback';
import { mockFormikContext } from '@custom-test-utils/formik_test_utils';

// Mock useFormikContext
jest.mock('formik', () => ({
  ...jest.requireActual('formik'),
  useFormikContext: () => mockFormikContext,
}));

const sampleErrorsIn = {
  metadata: {
    publication_date: "Missing data for required field.",
    resource_type: "Field may not be null.",
    rights: [
      { icon: "Unknown field." },
    ],
    creators: [
      {person_or_org: {
        identifiers: [ {identifier: "Invalid ORCID identifier"} ]
      }}
    ]
  },
  custom_fields: {
    "kcr:ai_usage": {
      ai_used: "Could not use AI"
    }
  }
};

const sampleInitialLabeledErrors = {
  "custom_fields.kcr:ai_usage": {
    "ai_used": "Could not use AI",
  },
  "metadata.creators": [
    {person_or_org: {
      identifiers: [
        {identifier: "Invalid ORCID identifier"}
      ]
    }}
  ],
  "metadata.publication_date": "Missing data for required field.",
  "metadata.resource_type": "Field may not be null.",
  "metadata.rights": [{"icon": "Unknown field."}],
};

const sampleLabeledErrorsAsArrays =  {
  "custom_fields.kcr:ai_usage": ["Could not use AI"],
  "metadata.creators": ["Invalid ORCID identifier"],
  "metadata.publication_date": ["Missing data for required field."],
  "metadata.resource_type": ["Field may not be null."],
  "metadata.rights": ["Unknown field."],
}

const sampleGroupedByLabel = {
  "Creators/Contributors": ["Invalid ORCID identifier"],
  "Licenses": ["Unknown field."],
  "Publication date": ["Missing data for required field."],
  "Resource type": ["Field may not be null."],
  "AI usage": ["Could not use AI"]
}

const sampleGroupedByLabelReadable = {
  "Creators/Contributors": ["Invalid ORCID identifier"],
  "Licenses": ["Unknown field."],
  "Publication date": ["Missing a value for a required field."],
  "Resource type": ["Field cannot be empty."],
  "AI usage": ["Could not use AI"]
}

const sampleValues = {
  "metadata": {
    "publication_date": "2021-01-01",
    "resource_type": "image",
  }
};

const sampleStartingState = {
  ...sampleState,
  deposit: {
    ...sampleState.deposit,
    config: {
      ...sampleState.deposit.config,
      custom_fields: {
        ...sampleState.deposit.config.custom_fields,
        error_labels: {},
      },
    },
    errors: sampleErrorsIn,
    actionState: "DRAFT_HAS_VALIDATION_ERRORS",
  },
  files: {},
};

describe('ErrorMessageHandler', () => {
  describe('collapseKeysIntoFieldLabels', () => {
    it('returns an object with field labels as keys', () => {
      const fieldLabelledErrors = ErrorMessageHandler.collapseKeysIntoFieldLabels(sampleErrorsIn);
      expect(fieldLabelledErrors).toEqual(sampleInitialLabeledErrors);
    })
  })

  describe('errorsToMessageArrays', () => {
    it('returns an error object with arrays of message strings as objects', () => {
      const errorMessages = ErrorMessageHandler.errorsToMessageArrays(sampleInitialLabeledErrors);
      expect(errorMessages).toEqual(sampleLabeledErrorsAsArrays);
    });
  });

  describe('groupMessagesByLabel', () => {
    it('returns an error object with error message lists combined if paths are mapped to the same label', () => {
      const groupedErrors = ErrorMessageHandler.groupMessagesByLabel(
        sampleLabeledErrorsAsArrays, defaultFieldLabels
      );
      expect(groupedErrors).toEqual(sampleGroupedByLabel);
    });
  });

  describe('toLabelledErrorMessages', () => {
    it('returns an array of labelled error messages', () => {
      const labelledErrorMessages = ErrorMessageHandler.toLabelledErrorMessages({...sampleErrorsIn}, defaultFieldLabels);
      expect(labelledErrorMessages).toEqual(sampleGroupedByLabelReadable);
    });
  });

  describe('makeErrorReadable', () => {
    it('converts error messages to more readable format', () => {
      expect(ErrorMessageHandler.makeErrorReadable("Missing data for required field."))
        .toBe("Missing a value for a required field.");
      expect(ErrorMessageHandler.makeErrorReadable("Field may not be null."))
        .toBe("Field cannot be empty.");
      expect(ErrorMessageHandler.makeErrorReadable("Some other error"))
        .toBe("Some other error");
    });
  });
});

describe('FormFeedback', () => {
  describe('renderErrorMessages', () => {
    it('returns a list of messages when there are multiple messages', () => {
      const { container } = renderWithProviders(
        <FormFeedback
          fieldPath="message"
          labels={sampleStartingState.deposit.config.custom_fields.error_labels}
          clientErrors={sampleErrorsIn}
          clientInitialErrors={sampleErrorsIn}
          clientInitialValues={sampleValues}
        />,
        { preloadedState: sampleStartingState }
      );
      expect(container).toHaveTextContent('Please correct the errors in the formPublication date: Missing a value for a required field.Resource type: Field cannot be empty.Licenses: Unknown field.Creators/Contributors: Invalid ORCID identifier');

      const header = container.querySelector('.header');
      expect(header).toHaveTextContent('Please correct the errors in the form');

      // Check that it renders a ul element
      const ul = container.querySelector('ul');
      expect(ul).toBeInTheDocument();

      // Check that it renders the correct number of li elements
      const lis = container.querySelectorAll('li');
      expect(lis).toHaveLength(5);

      // Check the content of each li
      expect(lis[0]).toHaveTextContent('Publication date: Missing a value for a required field.');
      expect(lis[1]).toHaveTextContent('Resource type: Field cannot be empty.');
      expect(lis[2]).toHaveTextContent('Licenses: Unknown field.');
      expect(lis[3]).toHaveTextContent('Creators/Contributors: Invalid ORCID identifier');
      expect(lis[4]).toHaveTextContent('AI usage: Could not use AI');
    });

    it('calls setFieldTouched with the correct arguments', () => {
      // Reset mock before test
      mockFormikContext.setFieldTouched.mockClear();

      renderWithProviders(
        <FormFeedback
          fieldPath="message"
          labels={sampleStartingState.deposit.config.custom_fields.error_labels}
          clientErrors={sampleErrorsIn}
          clientInitialErrors={sampleErrorsIn}
          clientInitialValues={sampleValues}
        />,
        { preloadedState: sampleStartingState }
      );

      // Verify setFieldTouched was called with the correct arguments
      expect(mockFormikContext.setFieldTouched).toHaveBeenCalledWith('custom_fields.kcr:ai_usage.ai_used', true);
      expect(mockFormikContext.setFieldTouched).toHaveBeenCalledWith('metadata.publication_date', true);
      expect(mockFormikContext.setFieldTouched).toHaveBeenCalledWith('metadata.resource_type', true);
      expect(mockFormikContext.setFieldTouched).toHaveBeenCalledWith('metadata.rights', true);
      expect(mockFormikContext.setFieldTouched).toHaveBeenCalledWith('metadata.creators', true);
    });

    it('deduplicates messages', () => {
      const sampleErrorsInWithDuplicates = {
        ...sampleErrorsIn,
        metadata: {
          ...sampleErrorsIn.metadata,
          rights: [...sampleErrorsIn.metadata.rights, { icon: "Unknown field." }],
        },
      };
      const sampleStartingStateWithDuplicates = {
        ...sampleStartingState,
        deposit: {
          ...sampleStartingState.deposit,
          errors: sampleErrorsInWithDuplicates,
        },
      };
      const { container } = renderWithProviders(
        <FormFeedback
          fieldPath="message"
          labels={sampleStartingState.deposit.config.custom_fields.error_labels}
          clientErrors={sampleErrorsInWithDuplicates}
          clientInitialErrors={sampleErrorsInWithDuplicates}
          clientInitialValues={sampleValues}
        />,
        { preloadedState: sampleStartingStateWithDuplicates }
      );

      // Check that it renders the correct number of unique li elements
      const lis = container.querySelectorAll('li');
      expect(lis).toHaveLength(5);

      // Check the content of each li
      expect(lis[0]).toHaveTextContent('Publication date: Missing a value for a required field.');
      expect(lis[1]).toHaveTextContent('Resource type: Field cannot be empty.');
      expect(lis[2]).toHaveTextContent('Licenses: Unknown field.');
      expect(lis[3]).toHaveTextContent('Creators/Contributors: Invalid ORCID identifier');
      expect(lis[4]).toHaveTextContent('AI usage: Could not use AI');
    });

    it('returns a single message when there is only one message', () => {
      const sampleErrorsInWithSingleMessage = {
        ...sampleErrorsIn,
        metadata: {
          publication_date: "Missing a value for a required field.",
        },
      };
      const sampleStartingStateWithSingleMessage = {
        ...sampleStartingState,
        deposit: {
          ...sampleStartingState.deposit,
          errors: sampleErrorsInWithSingleMessage,
        },
      };
      const { container } = renderWithProviders(
        <FormFeedback
          fieldPath="message"
          labels={sampleStartingState.deposit.config.custom_fields.error_labels}
          clientErrors={sampleErrorsInWithSingleMessage}
          clientInitialErrors={sampleErrorsInWithSingleMessage}
          clientInitialValues={sampleValues}
        />,
        { preloadedState: sampleStartingStateWithSingleMessage }
      );
      expect(container).toHaveTextContent('Publication date: Missing a value for a required field.');

      // Check that it does not render a nested ul element
      const ul = container.querySelector('ul ul');
      expect(ul).toBeNull();
    });

    it('handles empty array', () => {
      const startingStateWithEmptyErrors = {
        ...sampleStartingState,
        deposit: {
          ...sampleStartingState.deposit,
          errors: {},
        },
      };
      const { container } = renderWithProviders(
        <FormFeedback
          fieldPath="message"
          labels={sampleStartingState.deposit.config.custom_fields.error_labels}
          clientErrors={{}}
          clientInitialErrors={{}}
          clientInitialValues={sampleValues}
        />,
        { preloadedState: startingStateWithEmptyErrors }
      );
      expect(container).toBeEmptyDOMElement();
    });
  });
});