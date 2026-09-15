# Record access: requests and grants

Published works can restrict **metadata**, **files**, or both. How someone else
gets access depends on which of those is restricted.

## Restriction modes

| Mode | What visitors see | Typical use |
| ---- | ----------------- | ----------- |
| **Public metadata, restricted files** | Record landing page (title, authors, description, etc.); files are blocked | Share citation metadata while limiting downloads |
| **Fully restricted record** | No usable landing page for unauthorized users (permission denied / 403) | Keep the work private until access is given explicitly |

These settings live on the record’s access configuration (`record` and `files`
each public or restricted). Owners can also enable **allow user requests** and
**allow guest requests** on the record; those flags only matter for the
request flow described below.

## Access requests (requester-initiated)

Access **requests** are for the **public metadata + restricted files** case.

When a visitor can open the record page but cannot see files, and requests are
enabled for their role (signed-in user or guest), the landing page shows a
**Request access** form in the Files section. Submitting it creates a request
for the record owner to accept or decline.

On accept, the requester receives a **view** grant (signed-in users) or a
**secret link** (guests), which unlocks file access for that work.

```{important}
Access requests are **not** available for fully restricted records.

Creating a request requires that the requester can already **read** the
record’s metadata. If the whole record is restricted, unauthorized users never
reach a landing page with the form, and the backend refuses a user access
request for the same reason. Enabling “allow access requests” on a fully
restricted work does **not** change that.
```

## Access grants (owner- or manager-initiated)

Access **grants** (and secret links) are issued from the record owner’s or
manager’s side—for example via the Share / access UI on the record.

Grants **can** be used for fully restricted records. Someone who cannot see the
work at all can still be given access if an owner or manager creates a grant
(or secret link) for them. That is the supported path when a work’s metadata
must stay private until access is approved.

| Need | Mechanism |
| ---- | --------- |
| Visitor can see the record page but not files, and should ask for download access | Access **request** (if enabled on the record) |
| Work is fully restricted; someone needs access who cannot see it yet | Access **grant** or secret link from the owner/manager |

## Practical notes for operators

- If a user reports they cannot request access to a private work, check whether
  the **record** itself is restricted (not only the files). In that case they
  need a grant from the owner, not a request form.
- Accepting an access request grants **view** permission. For the common
  public-metadata case, that mainly unlocks files; the same permission level
  is what grants use to open fully restricted records when issued directly.
- Guest requests go through email verification before a request object is
  created; signed-in user requests are created immediately and notify the
  owner.
