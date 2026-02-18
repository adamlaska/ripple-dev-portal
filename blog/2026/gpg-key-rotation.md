---
category: 2026
date: "2026-02-17"
template: '../../@theme/templates/blogpost'
seo:
    title: GPG Key Rotation
    description: Ripple has rotated the GPG key used to sign rippled packages.
labels:
    - Advisories
markdown:
    editPage:
        hide: true
---
# GPG Key Rotation

Ripple has rotated the GPG key used to sign `rippled` packages. If you have an existing installation, you should download and trust the new key to prevent issues upgrading in the future. **Automatic upgrades will not work** until you have trusted the new key.

## Action Needed

Add and trust new key.

### Red Hat Enterprise Linux / CentOS

```bash
sudo rpm --import https://repos.ripple.com/repos/rippled-rpm/stable/repodata/repomd.xml.key
```

### Ubuntu / Debian

```bash
wget -q -O - "https://repos.ripple.com/repos/api/gpg/key/public" | apt-key add -
```
