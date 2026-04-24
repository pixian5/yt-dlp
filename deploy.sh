#!/bin/bash
set -e

echo "===== yt-dlp GUI 部署脚本 ====="

# 配置
APP_NAME="yt-dlp-gui"
PROJECT_DIR="/Users/x/code/yt-dlp"
BUILD_DIR="${PROJECT_DIR}/dist"
APP_DIR="/Applications/${APP_NAME}.app"
SPEC_FILE="${PROJECT_DIR}/yt-dlp-gui.spec"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 编译应用程序
echo ""
log_info "[1/6] 正在编译应用程序..."
cd "${PROJECT_DIR}"
source .venv/bin/activate

# 检查 PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    log_error "PyInstaller 未安装，正在安装..."
    pip install pyinstaller
fi

# 清理旧构建
log_info "清理旧构建..."
rm -rf dist build

# 使用 PyInstaller 编译
log_info "开始编译..."
pyinstaller "${SPEC_FILE}" --clean

# 检查编译结果
BUILT_APP="${BUILD_DIR}/${APP_NAME}.app"
if [ ! -d "${BUILT_APP}" ]; then
    log_error "编译失败，未找到应用程序: ${BUILT_APP}"
    exit 1
fi

log_info "编译成功！"

# 2. 关闭旧程序
echo ""
log_info "[2/6] 正在关闭旧程序..."
# 获取旧程序 PID
OLD_PIDS=$(pgrep -f "${APP_NAME}.app" || true)
if [ -n "$OLD_PIDS" ]; then
    log_warn "发现运行中的旧程序，PID: $OLD_PIDS"
    # 先尝试正常关闭
    echo "$OLD_PIDS" | xargs kill -TERM 2>/dev/null || true
    sleep 3
    # 检查是否还在运行
    NEW_PIDS=$(pgrep -f "${APP_NAME}.app" || true)
    if [ -n "$NEW_PIDS" ]; then
        log_warn "强制关闭旧程序..."
        echo "$NEW_PIDS" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    log_info "旧程序已关闭"
else
    log_info "没有运行中的旧程序"
fi

# 3. 删除旧程序
echo ""
log_info "[3/6] 正在删除旧程序..."
if [ -d "${APP_DIR}" ]; then
    rm -rf "${APP_DIR}"
    log_info "已删除旧程序: ${APP_DIR}"
else
    log_info "没有旧程序需要删除"
fi

# 4. 复制到应用程序目录
echo ""
log_info "[4/6] 正在复制到应用程序目录..."
cp -R "${BUILT_APP}" "${APP_DIR}"
log_info "已复制到: ${APP_DIR}"

# 5. 运行检测（10秒闪退检测）
echo ""
log_info "[5/6] 正在运行检测（10秒闪退检测）..."

# 启动程序
open "${APP_DIR}"
sleep 2

# 获取 PID
APP_PID=$(pgrep -f "${APP_NAME}.app/Contents/MacOS" | head -1)

if [ -z "$APP_PID" ]; then
    log_error "程序未能启动（可能是启动失败）"
    exit 1
fi

log_info "程序已启动，PID: $APP_PID"
log_info "等待 30 秒检测是否闪退..."

# 等待30秒
for i in {1..30}; do
    sleep 1
    if ! pgrep -q -f "${APP_NAME}.app/Contents/MacOS"; then
        log_error "程序已闪退！（在第 ${i} 秒）"
        exit 1
    fi
    echo -n "."
done
echo ""

log_info "检测通过：程序正常运行超过 30 秒"

# 关闭测试运行的程序
log_info "关闭测试实例..."
pkill -f "${APP_NAME}.app/Contents/MacOS" || true
sleep 1

# 6. Git 提交并推送
echo ""
log_info "[6/6] 正在提交并推送到 git..."

# 检查是否有更改
if git diff --quiet && git diff --cached --quiet; then
    log_warn "没有需要提交的更改"
else
    # 生成提交信息
    COMMIT_MSG="部署更新: $(date '+%Y-%m-%d %H:%M:%S')

- 更新 GUI 功能
- 自动部署构建

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"

    git add -A
    git commit -m "$COMMIT_MSG"

    log_info "推送到远程仓库..."
    git push

    log_info "已推送到 git"
fi

echo ""
echo "========================================"
log_info "部署完成！"
echo "========================================"
echo ""
echo "应用程序位置: ${APP_DIR}"
echo ""
echo "现在可以手动启动程序："
echo "  open \"${APP_DIR}\""
echo ""
