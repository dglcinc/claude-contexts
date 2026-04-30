# gh — workaround for macOS Security.framework TLS bug

## Symptom

`gh <anything>` fails with:

```
tls: failed to verify certificate: x509: OSStatus -26276
```

while `git push`, `curl`, and `openssl s_client` all reach api.github.com fine through the same network. `OSStatus -26276` = Apple's `errSSLPeerCertExpired`, but the cert chain is genuinely valid — it's a Go-on-darwin cgo cert validation bug interacting with this machine's keychain trust state.

## Root cause

Homebrew's `gh` bottle is built with `CGO_ENABLED=1`, so its TLS path goes through `Security.framework` via cgo. On this Mac that path is broken. Curl/git/openssl all use Homebrew OpenSSL with a bundled CA bundle, so they sidestep it.

A CGO-disabled `gh` build uses Go's pure-Go cert validation against `/etc/ssl/cert.pem` instead, which works.

## Fix

Build `gh` with `CGO_ENABLED=0` and put it where brew's gh used to live:

```bash
# 1. Prereqs
brew install go git-lfs

# 2. Build pure-Go gh.
#    GOPROXY=direct forces module fetches via git (which works) instead of
#    Go's HTTP client (which would hit the same Security.framework bug).
GOPROXY=direct GOSUMDB=off CGO_ENABLED=0 GOBIN=$HOME/go/bin \
  go install github.com/cli/cli/v2/cmd/gh@v2.89.0

# 3. Replace brew's gh
brew unlink gh
cp $HOME/go/bin/gh /opt/homebrew/bin/gh

# 4. Auth via insecure-storage (skips the bad keychain entry; writes to ~/.config/gh/hosts.yml)
gh auth login --hostname github.com --with-token --insecure-storage \
  < ~/OneDrive\ -\ DGLC/Claude/.github-token
```

## Pitfalls

- **Don't `brew install gh` to "upgrade" later.** That puts the broken cgo bottle back. To bump versions, repeat step 2 with the new `@v2.x.y` tag. If you must use brew, follow with `brew unlink gh && cp $HOME/go/bin/gh /opt/homebrew/bin/gh` again.
- **Don't drop `--insecure-storage`** when re-auth'ing. The macOS keyring entry on this machine is corrupted (`gh auth status` shows "The token in keyring is invalid" before this fix). `--insecure-storage` writes the token to `~/.config/gh/hosts.yml` instead.
- **Don't drop `GOPROXY=direct`** during the build — without it, `go install` itself hits the same TLS bug fetching modules from `proxy.golang.org`.
- **Sandbox**: Claude Code's sandbox blocks writes to `/opt/homebrew`, `~/go`, and `~/.cache`. The build steps above need `dangerouslyDisableSandbox: true`.

## Network context

This Mac runs Claude Code's session proxy at `http://localhost:<ephemeral>` (set as `HTTPS_PROXY` in the env). It's a passthrough proxy — `openssl s_client -proxy` through it sees the real GitHub Sectigo cert. So the proxy is *not* the source of the TLS failure; only Go's cgo cert path is.
