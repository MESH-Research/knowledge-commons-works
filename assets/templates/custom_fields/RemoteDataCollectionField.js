import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import apiClient from "@js/kcworks/utils/apiClient";
import { Accordion, AccordionTitle, AccordionContent, Icon, Popup, Menu, Segment, Input, Button, Dropdown, Message } from "semantic-ui-react";
import { FieldLabel } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";

export const TreeItem = ({ item, endpointId, path = "/", depth = 0, autoOpen = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [children, setChildren] = useState([]);
  const [loading, setLoading] = useState(false);

  const isDirectory = item.type === 'dir';
  const currentItemPath = path === "/" ? `/${item.name}` : `${path}/${item.name}`;

    useEffect(() => {
    let isMounted = true;
    const autoFetchChildren = async () => {
            if (autoOpen && isDirectory && !isOpen && children.length === 0) {
            setLoading(true);
            try {
                const response = await apiClient.get(`/api/globus/ls/${endpointId}`, {
                params: { path: currentItemPath },
                });
                if (isMounted) {
                setChildren(response.data);
                setIsOpen(true);
                }
            } catch (err) {
                console.error("Failed to auto-fetch folder contents:", err);
            } finally {
                if (isMounted) setLoading(false);
            }
        }
    };

    autoFetchChildren();

    return () => { isMounted = false; };
  }, [autoOpen, isDirectory, endpointId, currentItemPath]);

  const globusFileManagerUrl = isDirectory 
  ? `https://app.globus.org/file-manager?origin_id=${endpointId}&origin_path=${encodeURIComponent(currentItemPath + "/")}`
  : null;

  const handleGlobusLinkClick = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    try {
      await apiClient.get(`/api/globus/ls/${endpointId}`, {
        params: { path: currentItemPath },
      });
      window.open(globusFileManagerUrl, "_blank");
    } catch (err) {
      const status = err.response?.status;
      
      if (status === 403) {
        const confirmContinue403 = window.confirm(
          "You do not have permission to view this folder's contents. " +
          "If you continue to the Globus File Manager, you will see an empty directory. " +
          "\n\nDo you still want to continue?"
        );
        if (confirmContinue403) {
          window.open(globusFileManagerUrl, "_blank");
        }
      } else if (status === 401) {
        const confirm401 = window.confirm(
          "Your session has expired or you are unauthorized to perform this action. " +
          "\n\nWould you like to be redirected to the login page?"
        );
        if (confirm401) {
          window.location.href = "/globus/login";
        }
      } else {
        window.open(globusFileManagerUrl, "_blank");
      }
    }
  };

  const handleToggle = async () => {
    if (!isDirectory) return;

    const nextOpenState = !isOpen;
    setIsOpen(nextOpenState);

    if (nextOpenState && children.length === 0) {
      setLoading(true);
      try {
        const response = await apiClient.get(`/api/globus/ls/${endpointId}`, {
          params: { path: currentItemPath },
        });
        console.log("Fetched folder contents:", response.data);
        setChildren(response.data);
      } catch (err) {
        console.error("Failed to fetch folder contents:", err);
      } finally {
        setLoading(false);
      }
    }
  };

if (!isDirectory) {
    return (
      <div style={{ padding: '5px 0', marginLeft: `${depth > 0 ? 25 : 0}px`, display: 'flex', alignItems: 'center' }}>
        <Icon name="file outline" />
        <span style={{ flexGrow: 1, textAlign: "left" }}>{item.name}</span>
        <Popup
          content="Open in Globus"
          trigger={
            <a href={globusFileManagerUrl} onClick={handleGlobusLinkClick}>
              <Icon name="external alternate" style={{ marginLeft: '12px', color: '#2185d0' }} />
            </a>
          }
        />
      </div>
    );
  }

  return (
    <Accordion style={{ marginLeft: `${depth > 0 ? 15 : 0}px`, marginTop: '0' }}>
      <AccordionTitle
        as="button"
        type="button"
        active={isOpen}
        onClick={handleToggle}
        className="ui fluid transparent button file-tree-btn"
        style={{ padding: "5px 0", display: "flex", alignItems: "center" }}
      >
        <Icon 
          name={isOpen ? "angle down" : "angle right"} 
          style={{ minWidth: '20px', textAlign: 'center' }} 
        />
        <Icon name={isOpen ? "folder open" : "folder"} color="yellow" style={{ marginLeft: '4px', marginRight: '8px' }} />
        <span style={{ flexGrow: 1 }}>{item.name}</span>
        {isOpen && !loading && children.length === 0 && (
          <span style={{ fontSize: '0.8em', color: 'gray', marginLeft: '10px' }}>(Empty)</span>
        )}
        <Popup
          content="Open in Globus"
          trigger={
            <a href={globusFileManagerUrl} onClick={handleGlobusLinkClick}>
              <Icon name="external alternate" style={{ marginLeft: '12px', color: '#2185d0' }} />
            </a>
          }
        />
      </AccordionTitle>
      
      <AccordionContent active={isOpen} style={{ paddingTop: '0', paddingBottom: '0' }}>
        {loading ? (
          <div style={{ marginLeft: '25px', padding: '5px 0' }}>
            <Icon name="spinner" loading /> Loading...
          </div>
        ) : (
          children.map((child, idx) => (
            <TreeItem 
              key={`${depth}-${idx}`} 
              item={child} 
              endpointId={endpointId}
              path={currentItemPath} 
              depth={depth + 1} 
              autoOpen={false}
            />
          ))
        )}
      </AccordionContent>
    </Accordion>
  );
};

export const FileTree = ({ initialFiles, endpointId, fieldPath }) => {
  return (
    <div className="field">
      <div 
        className="field-label-class invenio-field-label rel-mb-2" 
        id={`${fieldPath}.fileTree.label`}
        style={{ fontWeight: "bold" }}
      >
        <Icon name="sitemap" /> Collection File Tree
      </div>
      <div style={{ marginTop: '10px' }}>
        {initialFiles && initialFiles.length > 0 ? (
          initialFiles.map((item, index) => (
            <TreeItem key={index} item={item} endpointId={endpointId} autoOpen={true} />
          ))
        ) : (
          <div className="ui message info">No files found in the root directory.</div>
        )}
      </div>
    </div>
  );
};

const RemoteDataCollectionField = ({ fieldPath }) => {
  const { values, setFieldValue } = useFormikContext();

  const [endpoints, setEndpoints] = useState([]);
  const [hasToken, setHasToken] = useState(false);
  const [loadingInitial, setLoadingInitial] = useState(true);

  const [rootFiles, setRootFiles] = useState([]);
  const [loadingTree, setLoadingTree] = useState(false);
  const [treeError, setTreeError] = useState(null);

  const [activeTab, setActiveTab] = useState("existing");

  // creating guest collection - tab 2
  const [bucketName, setBucketName] = useState("");
  const [mappedCollection, setMappedCollection] = useState("");
  const [isProvisioning, setIsProvisioning] = useState(false);
  const [provisionError, setProvisionError] = useState(null);

  const [globusState, setGlobusState] = useState({});

  useEffect(() => {
    const initialFormikValue = getIn(values, fieldPath, null);
    if (initialFormikValue) {
      try {
        setGlobusState(JSON.parse(initialFormikValue));
      } catch (e) {
        setGlobusState({ guest_collection_id: initialFormikValue });
      }
    }
  }, []);

  // watching for internal state changes and syncing them OUT to Formik
  useEffect(() => {
    if (Object.keys(globusState).length > 0) {
      setFieldValue(fieldPath, JSON.stringify(globusState));
    }
  }, [globusState, fieldPath, setFieldValue]);

  // helper function to safely update our internal React state
  const updateGlobusState = (newData) => {
    setGlobusState(prevState => ({ ...prevState, ...newData }));
  };

  const selectedCollection = globusState.guest_collection_id || "";

  useEffect(() => {
    apiClient.get('/globus/endpoints')
      .then((response) => {
        if (response.data.endpoints && response.data.endpoints.length > 0) {
            setMappedCollection(response.data.endpoints[0].id);
        }
        setHasToken(true);
        setEndpoints(response.data.endpoints || []);
      })
      .catch((err) => {
        setHasToken(false);
      })
      .finally(() => {
        setLoadingInitial(false);
      });
  }, []);

  useEffect(() => {
      if (!selectedCollection) return;

      setLoadingTree(true);
      setTreeError(null);

      apiClient.get(`/api/globus/ls/${selectedCollection}`, { params: { path: "/" } })
      .then((response) => {
          setRootFiles(response.data);
      })
      .catch((err) => {
          console.error("Failed to fetch root files for selected endpoint:", err);
          setTreeError("Failed to load directory contents. You may not have permission.");
      })
      .finally(() => {
          setLoadingTree(false);
      });
  }, [selectedCollection]);

  const handleProvision = async () => {
    if (!bucketName || !mappedCollection) return;
    setIsProvisioning(true);
    setProvisionError(null);

    try {
      const response = await apiClient.post('/api/globus/provision', {
        bucket_name: bucketName,
        mapped_collection_id: mappedCollection
      });
      
      // store new UUIDs into Formik JSON
      updateGlobusState({
        bucket_id: response.data.bucket_id,
        guest_collection_id: response.data.guest_collection_id,
        folder_path: response.data.path
      });
      
      // switch back to 'existing' tab to show the file tree for the new bucket
      setActiveTab("existing");
    } catch (err) {
      setProvisionError("Failed to provision bucket. Please try again.");
    } finally {
      setIsProvisioning(false);
    }
  };

  if (loadingInitial) {
    return (
      <div className="field mb-20">
        <FieldLabel
          htmlFor={fieldPath}
          id={`${fieldPath}.label`}
          icon="database"
          label="Globus Collection"
        />
        <div className="ui active centered inline loader"></div>
      </div>
    );
  }

  if (!hasToken) {
    const currentURL = window.location.pathname + window.location.search;
    const nextUrl = encodeURIComponent(currentURL);
    return (
      <div className="field mb-20">
        <FieldLabel
          htmlFor={fieldPath}
          id={`${fieldPath}.label`}
          icon="database"
          label="Globus Collection"
        />
        <div className="ui warning message">
          <p>You must connect your Globus account to upload a dataset.</p>
        </div>
        <a href={`/globus/login/start?next=${nextUrl}`} className="ui primary button">
          Log in with Globus
        </a>
      </div>
    );
  }

  const dropdownOptions = endpoints.map(ep => ({
    key: ep.id,
    value: ep.id,
    text: ep.display_name || ep.id
  }));

  return (
    <div className="field mb-20">
      <FieldLabel htmlFor={fieldPath} icon="cloud download" label="Globus Transfer Configuration" />
      <p style={{ color: "#666", marginBottom: "1em" }}>Link an existing Data Hub Guest Collection or provision a new bucket.</p>

      {/* THE TABS */}
      <Menu pointing secondary color="blue">
        <Menu.Item name="Select Existing Guest Collection" active={activeTab === "existing"} onClick={() => setActiveTab("existing")} />
        <Menu.Item name="Provision New Bucket" active={activeTab === "new"} onClick={() => setActiveTab("new")} />
      </Menu>

      <Segment attached="bottom">
        {/* TAB 1: EXISTING FILE TREE */}
        {activeTab === "existing" && (
          <div className="ui form">
            <div className="grouped fields" style={{ maxHeight: "200px", overflowY: "auto", paddingRight: "10px" }}>
              {endpoints.length > 0 ? endpoints.map((ep) => (
                <div className="field" key={ep.id}>
                  <div className="ui radio checkbox">
                    <input
                      id={`radio-${ep.id}`}
                      type="radio"
                      checked={selectedCollection === ep.id}
                      onChange={() => updateGlobusState({ guest_collection_id: ep.id })}
                      style={{ cursor: "pointer" }}
                    />
                    <label htmlFor={`radio-${ep.id}`} style={{ cursor: "pointer" }}>
                      {ep.display_name || ep.id}
                    </label>
                  </div>
                </div>
              )) : <Message info>No collections found on your account.</Message>}
            </div>

            {selectedCollection && (
              <div style={{ marginTop: "15px", padding: "15px", backgroundColor: "#f8f8f9", border: "1px solid #d4d4d5", borderRadius: "4px" }}>
                <div style={{ marginBottom: "15px" }}><strong>Active Collection:</strong> <code>{selectedCollection}</code></div>
                {loadingTree ? <div className="ui active centered inline loader"></div> 
                 : treeError ? <Message negative>{treeError}</Message> 
                 : <FileTree initialFiles={rootFiles} endpointId={selectedCollection} fieldPath={fieldPath} />}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: PROVISION NEW BUCKET */}
        {activeTab === "new" && (
          <div className="ui form">
            <div className="field">
              <label htmlFor="mappedCollectionDropdown">Parent Mapped Collection</label>
              <Dropdown
                id="mappedCollectionDropdown"
                selection
                fluid
                options={dropdownOptions}
                value={mappedCollection}
                onChange={(e, { value }) => setMappedCollection(value)}
              />
            </div>
            <div className="field">
              <label htmlFor="bucketNameInput">New Bucket / Folder Name</label>
              <Input
                id="bucketNameInput"
                placeholder="e.g., my-research-dataset"
                value={bucketName}
                onChange={(e) => setBucketName(e.target.value)}
              />
            </div>
            {provisionError && <Message negative>{provisionError}</Message>}
            <Button 
              primary 
              loading={isProvisioning} 
              disabled={isProvisioning || !bucketName}
              onClick={handleProvision}
            >
              Provision Bucket
            </Button>
          </div>
        )}
      </Segment>
    </div>
  );
};

export default RemoteDataCollectionField;