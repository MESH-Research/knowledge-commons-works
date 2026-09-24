import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithFormik, setupFormMocks } from '@custom-test-utils/formik_test_utils';
import { AccessRightField } from './AccessRightField';
import { setupStore } from '@custom-test-utils/redux_store';
import { Provider } from 'react-redux';

const renderComponent = (props = {}, storeOverrides = {}) => {
  const defaultProps = {
    fieldPath: "access",
    label: "Access",
    icon: "lock",
    record: {
      id: "test-record",
      access: {
        record: "public",
        files: "public"
      },
      // Component reads record.files.enabled for metadata-only detection.
      files: {
        enabled: true
      }
    },
    recordRestrictionGracePeriod: 30,
    allowRecordRestriction: true,
    // Metadata access section is gated on this prop.
    showMetadataAccess: true,
  };

  const store = setupStore({
    deposit: {
      editorState: {
        selectedCommunity: null
      },
      record: {
        id: "test-record",
        links: {
          access: "/api/records/test-record/access",
        },
        parent: {
          access: {
            settings: {
              allow_user_requests: false,
              allow_guest_requests: false,
            },
          },
        },
      },
      permissions: {
        can_manage: true,
        can_manage_record_access: true,
      },
      config: {
        groups_enabled: false,
      },
    },
    // Component reads files.entries from Redux (upload state).
    // Empty entries => metadata-only UI ("The record has no files.").
    // Seed one entry so "Files access" is shown by default.
    files: {
      entries: {
        "file-1": { name: "test.pdf", size: 1024 },
      },
    },
    ...storeOverrides,
  });

  const formMocks = setupFormMocks({
    access: {
      record: "public",
      files: "public"
    },
    files: {
      enabled: true
    },
    parent: {
      access: {
        settings: {
          allow_user_requests: false,
          allow_guest_requests: false,
        },
      },
    },
    links: {
      access: "/api/records/test-record/access",
    },
  });

  return renderWithFormik(
    <Provider store={store}>
      <AccessRightField {...defaultProps} {...props} />
    </Provider>,
    {
      initialValues: formMocks.values,
      values: formMocks.values
    }
  );
};

describe('AccessRightField', () => {
  it('renders the component with default props', () => {
    renderComponent();

    // Check for the label
    expect(screen.getByText('Access')).toBeInTheDocument();

    // Check for metadata access section
    expect(screen.getByText('Record access')).toBeInTheDocument();

    // Check for files access section
    expect(screen.getByText('Files access')).toBeInTheDocument();

    // Check for embargo access section
    expect(screen.getByText('Apply an embargo')).toBeInTheDocument();

    // Access requests only show for public metadata + restricted files
    expect(screen.queryByText('Allow access requests')).not.toBeInTheDocument();
  });

  it('shows access requests controls when files are restricted', () => {
    const formMocks = setupFormMocks({
      access: {
        record: "public",
        files: "restricted",
      },
      files: {
        enabled: true,
      },
      parent: {
        access: {
          settings: {
            allow_user_requests: false,
            allow_guest_requests: false,
          },
        },
      },
      links: {
        access: "/api/records/test-record/access",
      },
    });

    const store = setupStore({
      deposit: {
        editorState: {
          selectedCommunity: null,
        },
        record: {
          id: "test-record",
          links: {
            access: "/api/records/test-record/access",
          },
          parent: {
            access: {
              settings: {
                allow_user_requests: false,
                allow_guest_requests: false,
              },
            },
          },
        },
        permissions: {
          can_manage: true,
          can_manage_record_access: true,
        },
        config: {
          groups_enabled: false,
        },
      },
      files: {
        entries: {
          "file-1": { name: "test.pdf", size: 1024 },
        },
      },
    });

    renderWithFormik(
      <Provider store={store}>
        <AccessRightField
          fieldPath="access"
          label="Access"
          record={{
            id: "test-record",
            access: { record: "public", files: "restricted" },
            files: { enabled: true },
          }}
          recordRestrictionGracePeriod={30}
          allowRecordRestriction={true}
          showMetadataAccess={true}
        />
      </Provider>,
      {
        initialValues: formMocks.values,
        values: formMocks.values,
      }
    );

    expect(screen.getByText('Allow access requests')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
  });

  it('shows access requests after embargo restricts public files', async () => {
    renderComponent();

    expect(screen.queryByText('Allow access requests')).not.toBeInTheDocument();

    userEvent.click(screen.getByTestId('embargo-checkbox-component'));

    await waitFor(() => {
      expect(screen.getByText('Allow access requests')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
    });
  });

  it('renders without metadata access when showMetadataAccess is false', () => {
    renderComponent({ showMetadataAccess: false });

    // Check that metadata access section is not present
    expect(screen.queryByText('Record access')).not.toBeInTheDocument();

    // Check that files access section is still present
    expect(screen.getByText('Files access')).toBeInTheDocument();
  });

  // TODO: Finish once we resolve the issue with the community access
  // it('renders with community access when community is provided', () => {
  //   const community = {
  //     id: 'test-community',
  //     access: {
  //       visibility: 'restricted'
  //     }
  //   };
  //
  //   renderComponent({}, {
  //     deposit: { editorState: { selectedCommunity: community } },
  //   });
  //
  //   // Check that the record access is restricted when community access is restricted
  //   const recordAccess = screen.getByLabelText('Record access');
  //   expect(recordAccess).toHaveClass('disabled');
  //   // Check that the component renders with community access
  //   expect(screen.getByText('Files access')).toBeInTheDocument();
  // });

  it('renders with ghost community access', () => {
    const community = {
      id: 'test-community',
      is_ghost: true,
      access: {
        visibility: 'restricted'
      }
    };

    // Community comes from Redux deposit.editorState.selectedCommunity, not props.
    // Leave default files.entries so Files access (not metadata-only) is shown.
    renderComponent({}, {
      deposit: {
        editorState: {
          selectedCommunity: community
        }
      },
    });

    // Check that the component renders with public access (default for ghost communities)
    expect(screen.getByText('Files access')).toBeInTheDocument();
  });
});
