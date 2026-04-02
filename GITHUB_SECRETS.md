# GitHub Secrets 清单

这个项目当前的 GitHub Actions 需要以下 Secrets：

## 部署服务器连接
- `SERVER_HOST`：服务器 IP 或域名
- `SERVER_PORT`：SSH 端口，通常是 `22`
- `SERVER_USER`：SSH 登录用户名
- `SERVER_SSH_KEY`：用于部署的私钥内容（建议单独部署 key）
- `SERVER_APP_DIR`：服务器部署目录，例如 `/opt/tuoyue-erp`
- `APP_PORT`：服务对外监听端口，例如 `80` 或 `8080`

## Django / 应用配置
- `SECRET_KEY`：Django 生产环境密钥
- `ALLOWED_HOSTS`：例如 `erp.example.com,127.0.0.1,localhost`

## 数据库
- `DB_NAME`：数据库名
- `DB_USER`：数据库用户名
- `DB_PASSWORD`：数据库密码

## 可选但推荐
- `DB_PORT`：如果不是默认 3306，可额外改 workflow 使用
- `SENTRY_DSN`：如果你后续接入 Sentry
- `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN`：如果你不想用 GHCR，而想推 Docker Hub

## 不需要你额外手动创建的
- `GITHUB_TOKEN`：GitHub Actions 运行时会自动提供，用于推送 GHCR（前提是仓库/组织允许 packages 写入）
