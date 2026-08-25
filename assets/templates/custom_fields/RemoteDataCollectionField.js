import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import apiClient from "@js/kcworks/utils/apiClient";
import { Accordion, AccordionTitle, AccordionContent, Icon, Popup, Menu, Segment, Input, Button, Dropdown, Message, Grid } from "semantic-ui-react";
import { FieldLabel } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";

export const TreeItem = ({ item, endpointId, path = "/", depth = 0, autoOpen = false, autoCheckAccess = false, selectedFolder, onSelectFolder }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [children, setChildren] = useState([]);
  const [loading, setLoading] = useState(false);
  const [accessStatus, setAccessStatus] = useState('unknown'); 
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    let isMounted = true;
    if (autoCheckAccess && isDirectory && accessStatus === 'unknown') {
      const checkAccess = async () => {
        try {
          await apiClient.get(`/api/globus/ls/${endpointId}`, { params: { path: currentItemPath } });
          if (isMounted) setAccessStatus('allowed');
        } catch (err) {
          if (isMounted && (err.response?.status === 403 || err.response?.status === 401)) {
            setAccessStatus('denied');
          }
        }
      };
      checkAccess();
    }
    return () => { isMounted = false; };
  }, [autoCheckAccess, isDirectory, endpointId, currentItemPath, accessStatus]);

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

  const handleSelectClick = async (e) => {
    e.stopPropagation();
    e.preventDefault();

    if (accessStatus === 'allowed') {
      onSelectFolder(currentItemPath);
      return;
    }

    setLoading(true);
    try {
      await apiClient.get(`/api/globus/ls/${endpointId}`, { params: { path: currentItemPath } });
      setAccessStatus('allowed');
      onSelectFolder(currentItemPath);
    } catch (err) {
      if (err.response?.status === 403 || err.response?.status === 401) {
        setAccessStatus('denied');
      }
    } finally {
      setLoading(false);
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

  const showSelect = isHovered || selectedFolder === currentItemPath || loading || accessStatus === 'denied';

  return (
    <Accordion style={{ marginLeft: `${depth > 0 ? 15 : 0}px`, marginTop: '0' }}>
      <AccordionTitle
        as="div"
        active={isOpen}
        onClick={handleToggle}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="ui fluid transparent button file-tree-btn"
        style={{ padding: "5px 0", display: "flex", alignItems: "center", cursor: accessStatus === 'denied' ? "not-allowed" : "pointer" }}
      >
        <Icon 
          name={isOpen ? "angle down" : "angle right"} 
          style={{ minWidth: '20px', textAlign: 'center' }} 
        />
        <Icon name={isOpen ? "folder open" : "folder"} color="yellow" style={{ marginLeft: '4px', marginRight: '8px' }} />
        
        <span style={{ 
          flexGrow: 1, 
          textAlign: "left",
          fontWeight: selectedFolder === currentItemPath ? "bold" : "normal",
          color: selectedFolder === currentItemPath ? "#2185d0" : "inherit"
        }}>
          {item.name}
        </span>
        
        {isOpen && !loading && children.length === 0 && (
          <span style={{ fontSize: '0.8em', color: 'gray', marginLeft: '10px' }}>(Empty)</span>
        )}

        <div style={{ marginLeft: '15px', minWidth: '70px', textAlign: 'right', visibility: showSelect ? 'visible' : 'hidden' }}>
          {loading ? (
            <Icon name="spinner" loading color="blue" />
          ) : accessStatus === 'denied' ? (
            <span style={{ color: 'red', fontSize: '0.85em', fontWeight: 'bold' }}>Denied</span>
          ) : (
            <Button 
              size="mini" 
              compact 
              color={selectedFolder === currentItemPath ? "blue" : null}
              onClick={handleSelectClick}
            >
              {selectedFolder === currentItemPath ? "Selected" : "Select"}
            </Button>
          )}
        </div>

        {selectedFolder === currentItemPath && (
          <Popup
            content="Open in Globus"
            trigger={
              <a href={globusFileManagerUrl} onClick={handleGlobusLinkClick}>
                <Icon name="external alternate" style={{ marginLeft: '12px', color: '#2185d0' }} />
              </a>
            }
          />
        )}
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
              autoCheckAccess={false} 
              selectedFolder={selectedFolder}
              onSelectFolder={onSelectFolder}
            />
          ))
        )}
      </AccordionContent>
    </Accordion>
  );
};

export const FileTree = ({ initialFiles, endpointId, fieldPath, selectedFolder, onSelectFolder, netid, searchQuery }) => {
  let filteredFiles = initialFiles || [];
  if (searchQuery) {
    filteredFiles = filteredFiles.filter(f => f.name.toLowerCase().includes(searchQuery.toLowerCase()));
  }

  const suggestedFiles = [];
  const otherFiles = [];

  if (netid) {
    filteredFiles.forEach(f => {
      if (f.name.toLowerCase().startsWith(netid.toLowerCase())) {
        suggestedFiles.push(f);
      } else {
        otherFiles.push(f);
      }
    });
  } else {
    otherFiles.push(...filteredFiles);
  }

  const autoCheck = (initialFiles && initialFiles.length < 15);
  
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
        {/* Suggested Buckets */}
        {suggestedFiles.length > 0 && (
          <div style={{ marginBottom: '15px' }}>
            <h5 className="ui dividing header" style={{ color: "#2185d0" }}>Suggested Buckets (Your NetID)</h5>
            {suggestedFiles.map((item, index) => (
              <TreeItem 
                key={`suggested-${index}`} 
                item={item} 
                endpointId={endpointId} 
                autoOpen={false} 
                autoCheckAccess={autoCheck}
                selectedFolder={selectedFolder}
                onSelectFolder={onSelectFolder}
              />
            ))}
          </div>
        )}

        {/* All Other Buckets */}
        {otherFiles.length > 0 && (
          <div>
            {suggestedFiles.length > 0 && <h5 className="ui dividing header">All Other Buckets</h5>}
            {otherFiles.map((item, index) => (
              <TreeItem 
                key={`other-${index}`} 
                item={item} 
                endpointId={endpointId} 
                autoOpen={false}
                autoCheckAccess={autoCheck}
                selectedFolder={selectedFolder}
                onSelectFolder={onSelectFolder}
              />
            ))}
          </div>
        )}

        {filteredFiles.length === 0 && (
          <div className="ui message info">No files found matching your search.</div>
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

  const [netid, setNetid] = useState("");

  const [rootFiles, setRootFiles] = useState([]);
  const [loadingTree, setLoadingTree] = useState(false);
  const [treeError, setTreeError] = useState(null);

  const [searchQuery, setSearchQuery] = useState("");

  const [activeTab, setActiveTab] = useState("existing");
  const [isEditingMappedCollection, setIsEditingMappedCollection] = useState(true);

  const [selectedFolder, setSelectedFolder] = useState(null);

  const [matchedCollections, setMatchedCollections] = useState(null);
  const [checkingCollections, setCheckingCollections] = useState(false);
  const [checkError, setCheckError] = useState(null);
  const [accessDenied, setAccessDenied] = useState(false);

  // creating bucket - tab 2
  const [bucketName, setBucketName] = useState("");
  const [mappedCollection, setMappedCollection] = useState("");
  const [isProvisioning, setIsProvisioning] = useState(false);
  const [provisionError, setProvisionError] = useState(null);

  const [globusState, setGlobusState] = useState({});

  useEffect(() => {
    const initialFormikValue = getIn(values, fieldPath, null);
    if (initialFormikValue) {
      setIsEditingMappedCollection(false);
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
        setNetid(response.data.netid || "");
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
      setSelectedFolder(null);
      setSearchQuery("");

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

  useEffect(() => {
    if (!selectedCollection) {
      setMatchedCollections(null);
      return;
    }

    setCheckingCollections(true);
    setCheckError(null);

    apiClient.get('/api/globus/collections/check', {
      params: { endpoint_id: selectedCollection }
    })
    .then((response) => {
      setMatchedCollections(response.data.matches || []);
    })
    .catch((err) => {
      console.error("Failed to fetch guest collections:", err);
      setCheckError("Failed to getch your guest collections");
    })
    .finally(() => {
      setCheckingCollections(false);
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

      {/* 1. MAPPED COLLECTION SELECTOR (COLLAPSIBLE) */}
      {(!selectedCollection || isEditingMappedCollection) ? (
        <Segment style={{ backgroundColor: "#f8f8f9" }}>
          <h5 className="ui header">Select Mapped Collection</h5>
          <div className="grouped fields" style={{ maxHeight: "150px", overflowY: "auto" }}>
            {endpoints.length > 0 ? endpoints.map((ep) => (
              <div className="field" key={ep.id}>
                <div className="ui radio checkbox">
                  <input
                    id={`radio-${ep.id}`}
                    type="radio"
                    checked={selectedCollection === ep.id}
                    onChange={() => {
                      updateGlobusState({ guest_collection_id: ep.id });
                      setSelectedFolder(null);
                      setIsEditingMappedCollection(false); // NEW: Auto-collapse on selection
                    }}
                    style={{ cursor: "pointer" }}
                  />
                  <label 
                    htmlFor={`radio-${ep.id}`} 
                    onClick={() => {
                      if (selectedCollection === ep.id) {
                        setIsEditingMappedCollection(false);
                      }
                    }}
                    style={{ cursor: "pointer", fontWeight: selectedCollection === ep.id ? "bold" : "normal" }}
                  >
                    {ep.display_name || ep.id}
                  </label>
                </div>
              </div>
            )) : <Message info>No collections found on your account.</Message>}
          </div>
        </Segment>
      ) : (
        <Segment style={{ backgroundColor: "#f8f8f9", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <strong>Selected Mapped Collection: </strong> 
            {endpoints.find(ep => ep.id === selectedCollection)?.display_name || selectedCollection}
          </div>
          <Button size="small" basic onClick={() => setIsEditingMappedCollection(true)}>
            Change
          </Button>
        </Segment>
      )}

      {selectedCollection && !isEditingMappedCollection && (
        <>
          <Menu pointing secondary color="blue" style={{ marginTop: "20px" }}>
            <Menu.Item name="Select Existing Bucket" active={activeTab === "existing"} onClick={() => setActiveTab("existing")} />
            <Menu.Item name="Provision New Bucket" active={activeTab === "new"} onClick={() => setActiveTab("new")} />
          </Menu>

          <Segment attached="bottom">
            {/* TAB 1: SIDE-BY-SIDE PANELS */}
            {activeTab === "existing" && (
              <>
                {/* NEW: Full-width alert message moved above the grid */}
                <Message info icon>
                  <Icon name="info circle" />
                  <Message.Content>
                    Select a folder to create a new Guest Collection on it, or select an existing Guest Collection below.
                  </Message.Content>
                </Message>

                <Grid divided>
                  <Grid.Row>
                    {/* LEFT COLUMN: FILE TREE */}
                    <Grid.Column width={8}>
                      {loadingTree ? (
                        <div className="ui active centered inline loader"></div> 
                      ) : treeError ? (
                        <Message negative>{treeError}</Message> 
                      ) : (
                        <>
                          <Input 
                            icon="search" 
                            placeholder="Search buckets..." 
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            fluid
                            style={{ marginBottom: "15px" }}
                          />
                          <div style={{ maxHeight: "400px", overflowY: "auto", paddingRight: "10px" }}>
                            <FileTree 
                              initialFiles={rootFiles} 
                              endpointId={selectedCollection} 
                              fieldPath={fieldPath} 
                              selectedFolder={selectedFolder} 
                              onSelectFolder={setSelectedFolder} 
                              netid={netid}
                              searchQuery={searchQuery}
                            />
                          </div>
                        </>
                      )}
                    </Grid.Column>
                    
                    {/* RIGHT COLUMN: GUEST COLLECTIONS & CREATION */}
                    <Grid.Column width={8}>
                      {/* List Existing Collections */}
                      <h5 className="ui dividing header">Your Guest Collections</h5>
                      {checkingCollections ? (
                        <div className="ui active centered inline loader" style={{ margin: "20px" }}></div>
                      ) : checkError ? (
                        <Message negative>{checkError}</Message>
                      ) : matchedCollections && matchedCollections.length > 0 ? (
                        <div className="grouped fields" style={{ maxHeight: "250px", overflowY: "auto", marginBottom: "20px" }}>
                          {matchedCollections.map((mc) => (
                            <div className="field" key={mc.id}>
                              <div className="ui radio checkbox">
                                <input
                                  id={`radio-mc-${mc.id}`}
                                  type="radio"
                                  name="matched_guest_collection"
                                  checked={globusState.guest_collection_id === mc.id}
                                  onChange={() => updateGlobusState({ 
                                    guest_collection_id: mc.id
                                  })}
                                  style={{ cursor: "pointer" }}
                                />
                                <label htmlFor={`radio-mc-${mc.id}`} style={{ cursor: "pointer" }}>
                                  <strong>{mc.display_name || "Unnamed Collection"}</strong>
                                  <br /><span style={{ fontSize: "0.85em", color: "gray" }}>{mc.id}</span>
                                </label>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <Message warning>No guest collections found on this mapped endpoint.</Message>
                      )}

                      {/* Create New Collection Form */}
                      {selectedFolder && (
                        <div style={{ marginTop: "25px", padding: "15px", backgroundColor: "#f8f8f9", border: "1px solid #d4d4d5", borderRadius: "4px" }}>
                          <h5 className="ui header">Create a New Guest Collection</h5>
                          <div style={{ marginBottom: "15px" }}>
                            <strong>Target Folder:</strong> <code style={{ color: "#2185d0" }}>{selectedFolder}</code>
                          </div>
                          <div className="field">
                            <label htmlFor="newGuestCollectionName">Guest Collection Name</label>
                            <Input
                              id="newGuestCollectionName"
                              placeholder="e.g., My Research Data" 
                              value={bucketName}
                              onChange={(e) => setBucketName(e.target.value)}
                              fluid
                            />
                          </div>
                          <Button primary disabled={!bucketName}>
                            Create & Link Collection
                          </Button>
                        </div>
                      )}
                    </Grid.Column>
                  </Grid.Row>
                </Grid>
              </>
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
        </>
      )}
    </div>
  );
};

export default RemoteDataCollectionField;