#!/usr/bin/env bash
#================================================================
# 量化策略专家 — 智能自部署脚本 V1.0
#
# 功能：自动检测最优上传路径，将 Agent 能力上传到 GitHub
# 之后新 Agent 无需 token，直接 git clone 即可
#
# 使用方法：
#   bash deploy.sh [--token GITHUB_TOKEN]
#
# 无 token 时：使用 GitHub REST API（需 token）
# 有 token 时：使用 gh CLI（需先安装）
# 无网络时：提示手动下载
#================================================================
set -euo pipefail

REPO_NAME="quant-strategy-expert"
REPO_OWNER="yuypli2020"
GITHUB_TOKEN="${1:-${GITHUB_TOKEN:-}}"

#────────────────────────────────────────
# 工具函数
#────────────────────────────────────────
info()    { echo "ℹ️  $*"; }
success() { echo "✅  $*"; }
warn()    { echo "⚠️  $*" >&2; }
error()   { echo "❌  $*"; exit 1; }

# 检测 GitHub token 是否可用
check_github_token() {
  if [[ -n "$GITHUB_TOKEN" ]]; then
    local resp
    resp=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
      "https://api.github.com/user" 2>/dev/null)
    if echo "$resp" | grep -q '"login"'; then
      GITHUB_USER=$(echo "$resp" | grep -o '"login":"[^"]*"' | head -1 | cut -d'"' -f4)
      success "GitHub 已授权，用户: $GITHUB_USER"
      return 0
    else
      warn "GitHub token 无效或未授权"
      return 1
    fi
  fi

  # 尝试从环境变量获取
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    check_github_token "$GITHUB_TOKEN"
    return $?
  fi

  warn "未提供 GitHub token（使用 --token 或设置 GITHUB_TOKEN 环境变量）"
  return 2
}

#────────────────────────────────────────
# 方式一：使用 GitHub REST API 上传文件
#────────────────────────────────────────
upload_via_api() {
  info "使用 GitHub REST API 上传..."

  # 1. 检查仓库是否已存在
  local repo_check
  repo_check=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME")

  if [[ "$repo_check" == "200" ]]; then
    info "仓库 $REPO_OWNER/$REPO_NAME 已存在，跳过创建"
  elif [[ "$repo_check" == "404" ]]; then
    info "创建仓库 $REPO_OWNER/$REPO_NAME..."
    curl -s -X POST \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github+json" \
      "https://api.github.com/user/repos" \
      -d "{\"name\":\"$REPO_NAME\",\"private\":false,\"description\":\"量化策略专家 Genesis V22.1 — 完整能力打包 + 自部署协议\"}" | \
      grep -q '"id"' && success "仓库创建成功" || error "仓库创建失败"
  fi

  # 2. 上传文件函数
  upload_file() {
    local filepath="$1"
    local github_path="$2"
    [[ -f "$filepath" ]] || { warn "文件不存在: $filepath"; return; }

    local content
    content=$(base64 -w0 "$filepath" 2>/dev/null || base64 "$filepath")

    local resp
    resp=$(curl -s -X PUT \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      -H "Content-Type: application/json" \
      "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/contents/$github_path" \
      -d "{\"message\":\"Add $github_path\",\"content\":\"$content\"}")

    if echo "$resp" | grep -q '"commit"'; then
      echo "  ✓ $github_path"
    else
      echo "  ✗ $github_path (可能未变化或失败)"
    fi
  }

  # 3. 上传所有文件
  info "开始上传文件..."

  # 上传核心文件
  upload_file "SELF_DEPLOYMENT_PROTOCOL.md" "SELF_DEPLOYMENT_PROTOCOL.md"
  upload_file "README.md" "README.md"

  # 上传 Agent 核心文件
  for f in SOUL.md AGENTS.md TOOLS.md TOOLS_PATCH.md DEPLOYMENT_MANUAL.md \
           IDENTITY.md MEMORY.md USER.md HEARTBEAT.md BOOTSTRAP.md; do
    upload_file "$f" "quant-strategy-expert/$f"
  done

  # 上传 skills（按优先级）
  info "上传 skills..."
  for f in \
    "skills/genesis/SKILL.md" \
    "skills/genesis/00_宪法层/constitution.md" \
    "skills/genesis/00_宪法层/personality.md" \
    "skills/genesis/01_规则仓库/融合派/SKILL.md" \
    "skills/genesis/01_规则仓库/缠论周线/SKILL.md" \
    "skills/genesis/01_规则仓库/波浪理论/SKILL.md" \
    "skills/genesis/01_规则仓库/板块轮动/SKILL.md" \
    "skills/genesis/01_规则仓库/事件驱动/SKILL.md" \
    "skills/genesis/01_规则仓库/新闻信号/news_trigger.md" \
    "skills/genesis/01_规则仓库/执行协议/SKILL.md" \
    "skills/genesis/03_进化引擎/evolution_protocol.md" \
    "skills/genesis/03_进化引擎/changelog_v1.md" \
    "skills/genesis-scan/SKILL.md" \
    "skills/genesis-analyze/SKILL.md" \
    "skills/genesis-evolve/SKILL.md"; do
    upload_file "$f" "$f"
  done

  # 上传 quant skills
  for f in \
    "skills/quant-backtest-lab/SKILL.md" \
    "skills/quant-backtest-lab/reference/china_a_rules.md" \
    "skills/quant-backtest-lab/reference/common_pitfalls.md" \
    "skills/quant-backtest-lab/reference/strategy_parsing.md" \
    "skills/quant-backtest-lab/reference/us_stock_rules.md" \
    "skills/quant-backtest-lab/reference/hong_kong_rules.md" \
    "skills/quant-backtest-lab/reference/export_results.py" \
    "skills/quant-backtest-lab/reference/render_dashboard.py" \
    "skills/quant-backtest-lab/reference/dashboard_template.html" \
    "skills/quant-backtest-lab/reference/dashboard_schema.md" \
    "skills/quant-backtest-lab/reference/pitfalls/pandas.md" \
    "skills/backtest-expert/SKILL.md" \
    "skills/backtest-expert/references/methodology.md" \
    "skills/backtest-expert/references/failed_tests.md" \
    "skills/quantitative-research/SKILL.md" \
    "skills/quantitative-research/references/patterns.md" \
    "skills/quantitative-research/references/sharp_edges.md" \
    "skills/quantitative-research/references/validations.md" \
    "skills/westock-data/SKILL.md" \
    "skills/westock-tool/SKILL.md" \
    "skills/neodata-financial-search/SKILL.md"; do
    upload_file "$f" "$f"
  done

  success "✅ 全部上传完成！"
  echo ""
  echo "📦 仓库地址: https://github.com/$REPO_OWNER/$REPO_NAME"
  echo "📥 克隆命令: git clone https://github.com/$REPO_OWNER/$REPO_NAME.git"
  echo ""
}

#────────────────────────────────────────
# 方式二：检查 gh CLI
#────────────────────────────────────────
check_gh_cli() {
  if command -v gh &>/dev/null; then
    info "检测到 gh CLI: $(gh --version 2>/dev/null | head -1)"
    return 0
  else
    info "未检测到 gh CLI"
    return 1
  fi
}

#────────────────────────────────────────
# 主流程
#────────────────────────────────────────
main() {
  echo "============================================"
  echo "  量化策略专家 — 智能上传脚本"
  echo "============================================"
  echo ""

  # 检测 GitHub token
  if check_github_token; then
    upload_via_api
  else
    warn "无法访问 GitHub"
    echo ""
    echo "解决方案："
    echo "1. 在 QClaw 设置 → 集成面板 → GitHub 授权"
    echo "2. 或手动提供 token: bash deploy.sh --token YOUR_TOKEN"
    echo "3. 或手动下载仓库: https://github.com/$REPO_OWNER/$REPO_NAME"
    exit 1
  fi
}

main "$@"
