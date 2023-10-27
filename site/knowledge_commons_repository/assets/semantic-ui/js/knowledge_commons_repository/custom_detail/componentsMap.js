import { RecordTitle } from "./components/RecordTitle";
import { Citation } from "./components/Citation";
import { CitationSection } from "./sections/DetailSidebarCitationSection";
import { CommunitiesBanner } from "./components/CommunitiesBanner";
import { Creatibutors, CreatibutorsShortList } from "./components/Creatibutors";
import { Descriptions } from "./components/Descriptions";
import { DetailMainSubjectsSection } from "./sections/DetailMainSubjectsSection";
import { DetailSidebarSubjectsSection } from "./sections/DetailSidebarSubjectsSection";
import { FileListBox } from "./components/FileList";
import { FilePreview } from "./components/FilePreview";
import { PublishingDetails } from "./components/PublishingDetails";
import { SidebarDetailsSection } from "./sections/DetailSidebarDetailsSection";
import { SidebarDownloadSection } from "./sections/DetailSidebarDownloadSection";
import { VersionsDropdownSection, VersionsListSection } from "./sections/DetailSidebarVersionsSection";


const componentsMap = {
    "Citation": Citation,
    "CitationSection": CitationSection,
    "CommunitiesBanner": CommunitiesBanner,
    "Creatibutors": Creatibutors,
    "CreatibutorsShortList": CreatibutorsShortList,
    "Descriptions": Descriptions,
    "DetailMainSubjectsSection": DetailMainSubjectsSection,
    "DetailSidebarSubjectsSection": DetailSidebarSubjectsSection,
    "FileListBox": FileListBox,
    "FilePreview": FilePreview,
    "PublishingDetails": PublishingDetails,
    "RecordTitle": RecordTitle,
    "SidebarDetailsSection": SidebarDetailsSection,
    "SidebarDownloadSection": SidebarDownloadSection,
    "VersionsListSection": VersionsListSection,
    "VersionsDropdownSection": VersionsDropdownSection,
};

export { componentsMap };