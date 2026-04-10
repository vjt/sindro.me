# Remark42 Upgrade Guide

How to build and deploy Remark42 on m42 (FreeBSD) from source with embedded frontend.

## Prerequisites

- Go toolchain (already installed on m42)
- Node.js 16+ (already installed on m42)
- Source cloned at `~vjt/remark42`

## 1. Clone or update the source

```bash
# First time
git clone --depth 1 --branch v1.15.0 https://github.com/umputun/remark42.git ~/remark42

# Subsequent upgrades: fetch new tag
cd ~/remark42
git fetch --tags
git checkout v1.XX.X
```

## 2. Build the frontend

```bash
cd ~/remark42/frontend
CI=true npx pnpm@8 install --frozen-lockfile
```

Then build from the app directory:

```bash
cd ~/remark42/frontend/apps/remark42
npx pnpm@8 build
```

Output goes to `~/remark42/frontend/apps/remark42/public/` (~89 files).

## 3. Copy frontend to backend and fix placeholders

```bash
cp -r ~/remark42/frontend/apps/remark42/public/* ~/remark42/backend/app/cmd/web/

# Replace the REMARK_URL placeholder with our production URL (FreeBSD sed)
find ~/remark42/backend/app/cmd/web/ -regex '.*\.\(html\|js\|mjs\)$' \
  -exec sed -i '' 's|{% REMARK_URL %}|https://remark.sindro.me|g' {} \;
```

## 4. Build the Go binary

```bash
cd ~/remark42/backend
go build -o ~/remark42/remark42 -ldflags "-X main.revision=v1.XX.X" ./app
```

Verify:
```bash
~/remark42/remark42 version
# Should print: remark42 v1.XX.X
```

## 5. Deploy

```bash
sudo service remark42 stop
sudo cp /usr/local/sbin/remark42 /usr/local/sbin/remark42.bak   # backup
sudo cp ~/remark42/remark42 /usr/local/sbin/remark42
sudo service remark42 start
sudo service remark42 status
```

Check the log:
```bash
tail -10 /var/log/remark42.log
# Should say: "run file server, embedded"
```

## 6. Verify

```bash
curl -s http://127.0.0.1:8080/web/embed.mjs | head -1
# Should return JavaScript, not 404 or HTML stub
```

## Nginx (Sindrome theme CSS)

The nginx config for `remark.sindro.me` intercepts `/web/remark.css` and serves
the sindrome-themed version from the Hugo build output. See
`themes/sindrome/remark42-nginx.conf.sample` for the config.

The CSS file lives at `themes/sindrome/static/remark42/remark-sindrome.css` and
gets copied to `public/remark42/remark-sindrome.css` during Hugo build.

After a Hugo rebuild, the CSS is automatically picked up by nginx (no restart needed).

## Rollback

```bash
sudo service remark42 stop
sudo cp /usr/local/sbin/remark42.bak /usr/local/sbin/remark42
sudo service remark42 start
```

## Notes

- **Do not install packages globally** on m42. Use `npx pnpm@8` to run pnpm without installing it.
- The frontend build needs ~2GB RAM. m42 has plenty.
- The `go:embed web` directive in `backend/app/cmd/server.go` embeds the entire `web/` directory into the binary at compile time.
- Config lives at `/usr/local/etc/remark42.conf` (readable only by root).
- Data (boltdb, avatars, images, backups) lives at `/var/db/remark42/`.
