import { RecordTitle } from "./components/RecordTitle";
import { Citation } from "./components/Citation";
import { CitationSection } from "./sections/DetailSidebarCitationSection";
import { CommunitiesBanner } from "./components/CommunitiesBanner";
import { Creatibutors } from "./components/Creatibutors";
import { Descriptions } from "./components/Descriptions";
import { FileListBox } from "./components/FileList";
import { FilePreview } from "./components/FilePreview";
import { PublishingDetails } from "./components/PublishingDetails";
import { SidebarDetailsSection } from "./sections/DetailSidebarDetailsSection";
import { SidebarDownloadSection } from "./sections/DetailSidebarDownloadSection";
import { VersionsSection } from "./sections/DetailSidebarVersionsSection";


const componentsMap = {
    "Citation": Citation,
    "CitationSection": CitationSection,
    "CommunitiesBanner": CommunitiesBanner,
    "Creatibutors": Creatibutors,
    "Descriptions": Descriptions,
    "FileListBox": FileListBox,
    "FilePreview": FilePreview,
    "PublishingDetails": PublishingDetails,
    "RecordTitle": RecordTitle,
    "SidebarDetailsSection": SidebarDetailsSection,
    "SidebarDownloadSection": SidebarDownloadSection,
    "VersionsSection": VersionsSection,
};

export { componentsMap };