---
category: 2026
date: "2026-02-18"
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

Add Ripple's package-signing GPG key, then verify the fingerprint of the newly-added key.

{% tabs %}
{% tab label="Red Hat / CentOS" %}

```bash
sudo rpm --import https://repos.ripple.com/repos/rippled-rpm/stable/repodata/repomd.xml.key
rpm -qi gpg-pubkey-ab06faa6 | gpg --show-keys --fingerprint
```

{% /tab %}
{% tab label="Ubuntu / Debian" %}

```bash
wget -q -O - "https://repos.ripple.com/repos/api/gpg/key/public" | sudo apt-key add -
apt-key export AB06FAA6 | gpg --show-keys --fingerprint
```

{% /tab %}
{% /tabs %}

The output should include an entry for Ripple such as the following:

```
pub   ed25519 2026-02-16 [SC] [expires: 2033-02-14]
      E057 C1CF 72B0 DF1A 4559  E857 7DEE 9236 AB06 FAA6
uid                      TechOps Team at Ripple <techops+rippled@ripple.com>
sub   ed25519 2026-02-16 [S] [expires: 2029-02-15]
```
