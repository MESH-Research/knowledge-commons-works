import { RecordTitle } from "./components/RecordTitle";
import { Analytics } from "./components/Analytics";
import { Citation } from "./components/Citation";
import { CitationSection } from "./sections/DetailSidebarCitationSection";
import { CommunitiesBanner } from "./components/CommunitiesBanner";
import { ContentWarning } from "./components/ContentWarning";
import { Creatibutors, CreatibutorsShortList } from "./components/Creatibutors";
import { Descriptions } from "./components/Descriptions";
import { DetailMainSubjectsSection } from "./sections/DetailMainSubjectsSection";
import { DetailSidebarSubjectsSection } from "./sections/DetailSidebarSubjectsSection";
import { FileListBox } from "./components/FileList";
import { FilePreview } from "./components/FilePreview";
import { FilePreviewWrapper } from "./sections/DetailMainPreviewSection";
import { PublishingDetails } from "./components/PublishingDetails";
import { SidebarDetailsSection } from "./sections/DetailSidebarDetailsSection";
import { SidebarDownloadSection } from "./sections/DetailSidebarDownloadSection";
import { SidebarExportSection } from "./sections/DetailSidebarExportSection";
import { SidebarSharingSection } from "./sections/DetailSidebarSharingSection";
import { VersionsDropdownSection, VersionsListSection } from "./sections/DetailSidebarVersionsSection";


const componentsMap = {
    "Analytics": Analytics,
    "Citation": Citation,
    "CitationSection": CitationSection,
    "CommunitiesBanner": CommunitiesBanner,
    "ContentWarning": ContentWarning,
    "Creatibutors": Creatibutors,
    "CreatibutorsShortList": CreatibutorsShortList,
    "Descriptions": Descriptions,
    "DetailMainSubjectsSection": DetailMainSubjectsSection,
    "DetailSidebarSubjectsSection": DetailSidebarSubjectsSection,
    "FileListBox": FileListBox,
    "FilePreview": FilePreview,
    "FilePreviewWrapper": FilePreviewWrapper,
    "PublishingDetails": PublishingDetails,
    "RecordTitle": RecordTitle,
    "SidebarDetailsSection": SidebarDetailsSection,
    "SidebarDownloadSection": SidebarDownloadSection,
    "SidebarExportSection": SidebarExportSection,
    "SidebarSharingSection": SidebarSharingSection,
    "VersionsListSection": VersionsListSection,
    "VersionsDropdownSection": VersionsDropdownSection,
};

export { componentsMap };