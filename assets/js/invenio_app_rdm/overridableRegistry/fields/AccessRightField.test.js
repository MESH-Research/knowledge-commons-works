import React from 'react';
import { screen } from '@testing-library/react';
import { renderWithFormik } from '@custom-test-utils/formik_test_utils';
import { AccessRightFieldCmp } from './AccessRightField';
import { setupStore } from '@custom-test-utils/redux_store';
import { Provider } from 'react-redux';

const renderComponent = (props = {}) => {
  const defaultProps = {
    fieldPath: "access",
    label: "Access",
    icon: "lock",
    record: {
      id: "test-record",
      access: {
        record: "public",
        files: "public"
      }
    },
    recordRestrictionGracePeriod: 30,
    allowRecordRestriction: true
  };

  const store = setupStore({
    deposit: {
      editorState: {
        selectedCommunity: null
      }
    }
  });

  return renderWithFormik(
    <Provider store={store}>
      <AccessRightFieldCmp {...defaultProps} {...props} />
    </Provider>,
    {
      initialValues: {
        access: {
          record: "public",
          files: "public"
        }
      }
    }
  );
};

describe('AccessRightField', () => {
  it('renders the component with default props', () => {
    renderComponent();

    // Check for the label
    expect(screen.getByText('Access')).toBeInTheDocument();

    // Check for the icon
    expect(screen.getByText('Access').closest('label')).toHaveClass('icon');

    // Check for metadata access section
    expect(screen.getByText('Metadata access')).toBeInTheDocument();

    // Check for files access section
    expect(screen.getByText('Files access')).toBeInTheDocument();

    // Check for embargo access section
    expect(screen.getByText('Embargo')).toBeInTheDocument();
  });

  it('renders without metadata access when showMetadataAccess is false', () => {
    renderComponent({ showMetadataAccess: false });

    // Check that metadata access section is not present
    expect(screen.queryByText('Metadata access')).not.toBeInTheDocument();

    // Check that files access section is still present
    expect(screen.getByText('Files access')).toBeInTheDocument();
  });

  it('renders with community access when community is provided', () => {
    const community = {
      id: 'test-community',
      access: {
        visibility: 'restricted'
      }
    };

    renderComponent({ community });

    // Check that the component renders with community access
    expect(screen.getByText('Files access')).toBeInTheDocument();
  });

  it('renders with ghost community access', () => {
    const community = {
      id: 'test-community',
      is_ghost: true,
      access: {
        visibility: 'restricted'
      }
    };

    renderComponent({ community });

    // Check that the component renders with public access (default for ghost communities)
    expect(screen.getByText('Files access')).toBeInTheDocument();
  });
});