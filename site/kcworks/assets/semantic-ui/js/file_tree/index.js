import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import apiClient from "./apiClient";
import { Accordion, AccordionTitle, AccordionContent, Icon } from "semantic-ui-react";

const TreeItem = ({ item, endpointId, path = "/", depth = 0, autoOpen = false }) => {
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
        {item.name}
        <a 
          href={globusFileManagerUrl} 
          onClick={handleGlobusLinkClick}
          title="Open parent folder in Globus File Manager"
        >
          <Icon name="external alternate" style={{ marginLeft: '10px', color: '#2185d0' }} />
        </a>
      </div>
    );
  }

  return (
    <Accordion style={{ marginLeft: `${depth > 0 ? 15 : 0}px`, marginTop: '0' }}>
      <AccordionTitle
        active={isOpen}
        onClick={handleToggle}
        style={{ display: 'flex', alignItems: 'center', padding: '5px 0' }}
      >
        <Icon name={isOpen ? "angle down" : "angle right"} />
        <Icon name={isOpen ? "folder open" : "folder"} color="yellow" />
        <span style={{ flexGrow: 1 }}>{item.name}</span>
        {isOpen && !loading && children.length === 0 && (
          <span style={{ fontSize: '0.8em', color: 'gray', marginLeft: '10px' }}>(Empty)</span>
        )}
        <a 
          href={globusFileManagerUrl} 
          onClick={handleGlobusLinkClick}
          title="Open in Globus File Manager"
        >
          <Icon name="external alternate" style={{ marginLeft: '10px', color: '#2185d0' }} />
        </a>
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

const FileTree = ({ initialFiles, endpointId }) => {
  return (
    <div>
      <h3 className="ui header"><i className="sitemap icon"></i> Collection File Tree</h3>
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

const CollectionSelector = ({ endpoints, hasToken }) => {
  const [selectedCollection, setSelectedCollection] = useState("");
  const [rootFiles, setRootFiles] = useState([]);
  const [loadingTree, setLoadingTree] = useState(false);
  const [treeError, setTreeError] = useState(null);

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

  if (!hasToken) {
    return (
      <div className="ui segment">
        <h3 className="ui header">Select a Globus Collection</h3>
        <div className="ui warning message">
          <p>You must connect your Globus account to upload a dataset.</p>
        </div>
        <a href="/globus/login" className="ui primary button">
          Log in with Globus
        </a>
      </div>
    );
  }

  return (
    <div className="ui segment">
      <h3 className="ui header">Select a Globus Collection</h3>
      
      <div className="ui form">
        <div className="grouped fields" style={{ maxHeight: "200px", overflowY: "auto", paddingRight: "10px" }}>
          {endpoints && endpoints.length > 0 ? (
            endpoints.map((ep) => (
              <div className="field" key={ep.id}>
                <div className="ui radio checkbox">
                  <input
                    type="radio"
                    name="globus_collection"
                    id={`radio-${ep.id}`}
                    value={ep.id}
                    checked={selectedCollection === ep.id}
                    onChange={(e) => setSelectedCollection(e.target.value)}
                    style={{ cursor: "pointer" }}
                  />
                  <label htmlFor={`radio-${ep.id}`} style={{ cursor: "pointer" }}>
                    {ep.display_name || ep.id}</label>
                </div>
              </div>
            ))
          ) : (
            <div className="ui message info">No collections found on your account.</div>
          )}
        </div>
      </div>

      {selectedCollection && (
        <div className="ui segment" style={{ marginTop: "15px" }}>
          <div style={{ padding: "10px", backgroundColor: "#f8f8f9", border: "1px solid #d4d4d5", borderRadius: "4px", marginBottom: "15px" }}>
            <strong>Selected Collection ID:</strong> <br/>
            {selectedCollection}
          </div>
            {loadingTree ? (
                <div className="ui active centered inline loader"></div>
            ) : treeError ? (
                <div className="ui negative message">{treeError}</div>
            ) : (
                <FileTree initialFiles={rootFiles} endpointId={selectedCollection} />
            )}
        </div>
      )}
    </div>
  );
};

// --- MOUNTING LOGIC ---

const selectorElement = document.getElementById("globus-collection-selector");
if (selectorElement) {
  try {
    const endpointsData = JSON.parse(selectorElement.dataset.endpoints || "[]");
    const hasToken = selectorElement.dataset.hasToken === "true";

    ReactDOM.render(
      <CollectionSelector endpoints={endpointsData} hasToken={hasToken} />,
      selectorElement
    );
  } catch (err) {
    console.error("Failed to initialize CollectionSelector:", err);
  }
}
