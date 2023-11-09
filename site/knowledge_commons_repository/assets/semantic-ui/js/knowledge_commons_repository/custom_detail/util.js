
const filterPropsToPass = (topLevelProps, propList) => {
  const passedProps = Object.keys(topLevelProps)
    .filter((key) => propList.includes(key))
    .reduce((obj, key) => {
      obj[key] = topLevelProps[key];
      return obj;
    }, {});
  return passedProps;
};

const addPropsFromChildren = (children, props) => {
  props = props ? props : [];
  if (children) {
    props = children.reduce((acc, subsection) => {
      acc = subsection.props ? [...acc, ...subsection.props] : acc;
      return acc;
    }, props);
    props = props.reduce((acc, prop) => {
      if (!acc.includes(prop)) {
        acc.push(prop);
      }
      return acc;
    }, []);
  }
  return props;
}

const formatBytes = (bytes, decimals=2) => {
  if (!+bytes) return "0 Bytes";
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

// FIXME: duplicating idutils/__init__.py:to_url which calls
// idutils/__init__.py:normalize_pid but we aren't doing the normalization
function toPidUrl(pid, scheme, landingUrls) {
  if (landingUrls.hasOwnProperty(scheme)) {
    if (scheme === "gnd" && pid.startsWith("gnd:")) {
      pid = pid.slice("gnd:".length);
    }
    if (scheme === "urn" && !pid.toLowerCase().startsWith("urn:nbn:")) {
      return "";
    }
    if (scheme === "ascl") {
      pid = pid.split(":")[1];
    }
    if (scheme === "viaf" && pid.startsWith("viaf:")) {
      pid = pid.slice("viaf:".length);
    }
    return `${landingUrls[scheme]}${pid}`;
  } else if (["purl", "url"].includes(scheme)) {
    return pid;
  }
  return "";
}

function getFileTypeIconName(filename) {
  const extension = filename.split('.').pop().toLowerCase();
  switch (extension) {
    case 'pdf':
      return 'file pdf outline';
    case 'doc':
    case 'docx':
      return 'file word outline';
    case 'xls':
    case 'xlsx':
      return 'file excel outline';
    case 'ppt':
    case 'pptx':
      return 'file powerpoint outline';
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
      return 'file image outline';
    case 'mp3':
    case 'wav':
      return 'file audio outline';
    case 'mp4':
    case 'avi':
    case 'mov':
      return 'file video outline';
    case 'txt':
      return 'file text outline';
    default:
      return 'file outline';
  }
}

export { addPropsFromChildren, filterPropsToPass, formatBytes, getFileTypeIconName, toPidUrl };