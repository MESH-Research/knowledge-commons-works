# Feature Highlights

## Powerful tools for collaboration through the research lifecycle

- **Record versioning**, with persistent access to earlier versions
- **Metadata-only records** allow inclusion of works stored elsewhere, making them discoverable and allowing them to appear in institutional collections
- **Non-public draft records** and **restricted-access** published records support the need for privacy during some phases of the research and editorial cycles.
    - DOIs can be reserved but only registered when record becomes public
    - **Access grants** for fine-grained access control to restricted and draft works
- Flexible **public or private collections** supporting both open-access publication and private collaboration during the research and writing phases.
    - Assign users permissions as collection readers, curators, or managers
    - **Sub-collections** (coming in 2026) will allow for, e.g., collections for academic units, departments, and teams within a parent institutional collection

## Safe, solid, and reliable

- Better than 99.9% uptime in 2025
- Regular backups of file content and metadata
- Long-term cold storage backups (coming 2025)
- Industry-standard security practices

## Rich metadata

- Based on the **DataCite** schema
- On-demand instant access in a variety of **other standard formats** via UI and API
    - DataCite, MarcXML, DCAT XML, Citation Style Language, BibTeX, Dublin Core XML, GeoJSON, KCWorks/InvenioRDM
    - Including JSON, JSON-LD, XML, and CSV options
- Support for a **wide variety of resource types **with extensions to DataCite's schema
    - including some that are poorly served by traditional repositories (e.g., 3d models, podcasts, performances, blog posts, peer reviews, legal comments, physical objects, etc.)
    - All DataCite compatible and keyed to other resource type vocabularies (COAR, CSL, EUREPO, Schema.org) for easy transformation and export
- Acknowledgement of a **wide variety of contributor roles **with a DataCite compatible custom vocabulary.
    - Allows clear identification of supporting roles (e.g., editor, producer, researcher, transcriber), administrative roles (e.g., committee member, data manager), and creative contributions (e.g., artisan, choreographer, performer)
- Comprehensive **subject vocabularies**
    - FAST subject headings (over 2 million subjects across 9 facets)
    - Homosaurus subjects for better coverage of LGBTQIA+ topics
    - Complemented by free user-defined keywords
- Auto-generate **citations and bibliographies** via UI or API
    - APA, Harvard, MLA, Vancouver, Chicago, IEEE

## Interoperable

### Standard **identifiers**

- Every public work assigned a **DataCite-registered DOI**
    - A "concept DOI" for the work as a whole that always points to its newest version.
    - A separate DOI for each version of the work, allowing precise reference to a specific version
- Every work is also assigned an **OAI** identifier for use in the OAI-PMH protocol
- For other entities
    - **ORCID** for individuals
    - **ROR** for institutions and organizations
    - **OFR** for funders
    - **iso639** for languages

### Standard **protocols** supported

- **OAI-PMH** feeds
- **FAIR signposting**, providing machine-readable documentation of the metadata formats, media, and resources available for each work
- **IIIF manifest** for image resource types, accessible via public API
- **COAR Notify** (coming 2026)

### Embedded metadata in a variety standard formats

- Meta tags (opengraph, twitter, google/highwire)
- schema.org (embedded JSON-LD)

### Integrations for standard services and tools

- Deposits sync to a user's **ORCID profile** (if they opt-in for DataCite-ORCID sync)
- Research tools like **Zotero** can harvest metadata and files from detail pages
- **Github repository** integration (coming late 2025)

### Indexed by search engines and aggregators

- Google search
- DataCite
- Google Scholar (spring 2025)
- CORE.ac.uk (summer 2025)
- OpenAlex (later 2025?)

### Powerful APIs

- Public records API
    - Retrieve documents individually or in bulk, with powerful **search queries**
    - Return **metadata objects** (any supported export format) or formatted** citations/bibliography** (any supported citation format)
- Public collections API
    - search for collections and retrieve metadata about them
    - retrieve the records in a collection
    - retrieve public members of a collection's team
- **OAI-PMH feeds**
    - Dedicated feeds for **each institutional collection** and sub-collection
    - **Custom feeds** can be created for any query
- More APIs for **Authorized Users**
    - Self-managed **OAuth tokens** for API access based on a user account's permissions
    - **Create, update and manage** works, collections, collection membership
    - Retrieve restricted or draft records (based on user's permissions)
- **Import API** for member institutions
    - **Streamlined bulk import** of metadata and files for multiple works in one API request

## Flexible, powerful file handling

- **Multiple files** per work: up to 100 files attached to one record
- **Up to 500 GB** combined storage space per work, allowing storage of small research datasets
    - More efficient transfer for very large files coming in 2026
- Attach **any file type** for download.
- **In place previewers** for select file formats
    - Robust pdf viewer with navigation controls, full-screen view
    - Text documents (markdown with mathematical formulas are rendered
    - Image file viewer (gif, jpg, png)
    - Audio and video file players (mp3, wav, aac, flac, mp4, webm)
    - Zip archive viewer (lists zip archive contents)
    - Static code viewers for jupyter notebooks, XML/html source code, JSON
    - CSV data previewed in table view
    - GPX spatial data (coming in 2026)
- Download a work's files as **a single zip archive**

## Rich statistics for works and collections

- Compliant with MakeDataCount ([Make Data Count](https://makedatacount.org/)) and COUNTER ([COUNTER](https://www.projectcounter.org/)) standards
- Usage stats **for individual works** (all versions and each version separately) on detail pages
    - Total detail page views, total downloads, and total download volume
- Dashboards for institutions, collections, sub-collections (summer 2025)
    - Track works added to collection, aggregate usage stats for collection
    - Filter stats based on time period, resource type, creator affiliation, etc.
    - View trends over time
    - With clear, engaging data visualizations
- Dashboards for individual contributors (summer 2025)
    - All the same kind of data, for an individual user's works
    - Viewable by institutional admins
- Citations (2025)
    - We plan to add available citation data from DataCite and OpenAlex, but this will be partial and incomplete and must be used with caution.
    - Creators can add a record of incoming citations to their own works.

## Connections with **KC's larger suite of tools**

- Works and collections are discoverable through **KCWorks central search** as well as **KC's unified platform search**
- Collections can be **linked to KC groups** for connected discussion forums, group sites, etc.
- KCWorks on **KCProfiles**: customizable display of a user's work and statistics on their KC profile (summer 2025)
- A **KCWorks WordPress plugin** to display sets of works on any KC site (late 2025)
- Promotion of recent and highlighted works on KC sites and social media