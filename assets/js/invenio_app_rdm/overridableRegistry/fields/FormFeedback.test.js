import React from 'react';
import { render } from '@testing-library/react';
import { FormFeedback, errorsToMessageArrays, toLabelledErrorMessages, collapseKeysIntoFieldLabels, groupMessagesByLabel } from './FormFeedback';

import { renderWithProviders } from '@custom-test-utils/redux_test_utils';
import { sampleState } from '@custom-test-utils/redux_store';


const defaultLabels = {
  "files.enabled": "Files",
  "metadata.resource_type": "Resource type",
  "metadata.title": "Title",
  "metadata.additional_titles": "Additional titles",
  "metadata.publication_date": "Publication date",
  "metadata.creators": "Creators/Contributors",
  "metadata.contributors": "Creators/Contributors",
  "metadata.description": "Abstract/Description",
  "metadata.additional_descriptions": "Additional descriptions",
  "metadata.rights": "Licenses",
  "metadata.languages": "Languages",
  "metadata.dates": "Dates",
  "metadata.version": "Version",
  "metadata.publisher": "Publisher",
  "metadata.related_identifiers": "Related works",
  "metadata.references": "References",
  "metadata.identifiers": "Alternate identifiers",
  "metadata.subjects": "Keywords and subjects",
  "access.embargo.until": "Embargo until",
  "pids.doi": "DOI",
  "pids": "DOI",
};


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
  }
};

const sampleInitialLabeledErrors = {
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
  "pids": {}
};

const sampleLabeledErrorsAsArrays =  {
  "metadata.creators": ["Invalid ORCID identifier"],
  "metadata.publication_date": ["Missing data for required field."],
  "metadata.resource_type": ["Field may not be null."],
  "metadata.rights": ["Unknown field."], "pids": []
}

const sampleGroupedByLabel = {
  "Creators/Contributors": ["Invalid ORCID identifier"],
  "Licenses": ["Unknown field."],
  "Publication date": ["Missing data for required field."],
  "Resource type": ["Field may not be null."],
  "DOI": []
}

const sampleGroupedByLabelReadable = {
  "Creators/Contributors": ["Invalid ORCID identifier"],
  "Licenses": ["Unknown field."],
  "Publication date": ["Missing a value for a required field."],
  "Resource type": ["Field cannot be empty."],
  "DOI": []
}

const sampleErrorsOut = [
  {
    field: "metadata.publication_date",
    messages: ["Missing a value for a required field."],
  },
  { field: "metadata.resource_type", messages: ["Field may not be null."] },
  { field: "metadata.rights.0.icon", messages: ["Unknown field."] },
];

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

describe('collapseKeysIntoFieldLabels', () => {
  it('returns an object with field labels as keys', () => {
    const fieldLabelledErrors = collapseKeysIntoFieldLabels(sampleErrorsIn);
    expect(fieldLabelledErrors).toEqual(sampleInitialLabeledErrors);
  })
})

describe('errorsToMessageArrays', () => {
  it('returns an error object with arrays of message strings as objects', () => {
    const errorMessages = errorsToMessageArrays(sampleInitialLabeledErrors);
    expect(errorMessages).toEqual(sampleLabeledErrorsAsArrays);
  });
});

describe('groupMessagesByLabel', () => {
  it('returns an error object with error message lists combined if paths are mapped to the same label', () => {
    const groupedErrors = groupMessagesByLabel(
      sampleLabeledErrorsAsArrays, defaultLabels
    );
    expect(groupedErrors).toEqual(sampleGroupedByLabel);
  });
});

describe('toLabelledErrorMessages', () => {
  it('returns an array of labelled error messages', () => {
    const labelledErrorMessages = toLabelledErrorMessages({...sampleErrorsIn}, defaultLabels);
    expect(labelledErrorMessages).toEqual(sampleGroupedByLabelReadable);
  });
});

describe('FormFeedback', () => {
  describe('renderErrorMessages', () => {
    it('returns a single message when there is only one message', () => {
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
      expect(container).toHaveTextContent('Please correct the errors in the form.Publication date: Missing a value for a required field.Resource type: Field cannot be empty.Licenses: Unknown field.Creators/Contributors: Invalid ORCID identifierDOI:');

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
      expect(lis[4]).toHaveTextContent('DOI:');
    });

    it('deduplicates messages', () => {
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

      // Check that it renders the correct number of unique li elements
      const lis = container.querySelectorAll('li');
      expect(lis).toHaveLength(2);

      // Check the content of each li
      expect(lis[0]).toHaveTextContent('Error 1');
      expect(lis[1]).toHaveTextContent('Error 2');
    });

    it('handles empty array', () => {
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
      expect(container).toBeEmptyDOMElement();
    });
  });
});