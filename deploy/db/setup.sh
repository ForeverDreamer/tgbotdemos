#!/bin/bash

# chmod u+x setup.sh
# 设置脚本在遇到任何错误时退出，并开启调试模式（命令回显）
set -e
set -x

# 捕获错误并打印日志
trap 'log "脚本执行中发生错误，已中止。"' ERR

# 日志函数，打印带时间戳的日志信息
log() {
    set +x  # 临时禁用命令回显
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    set -x  # 重新启用命令回显
}

# 检查并设置 Redis 数据目录
setup_redis_directory() {
    # 如果 .env 文件不存在，直接退出
    [ -f "./.env" ] || { echo "错误：.env 文件不存在，请创建 .env 文件" >&2; exit 1; }
    # 从 .env 文件中读取 redis_dir 的值
    local redis_dir
    redis_dir=$(grep -E '^REDIS_DIR=' ./.env | cut -d '=' -f 2)
    # 检查 redis_dir 是否为空
    [ -n "$redis_dir" ] || { echo "错误：.env 文件中未找到 redis_dir 的值。" >&2; exit 1; }

    if [ ! -d "$redis_dir" ]; then
        mkdir -p "$redis_dir"
        log "Redis 数据目录已创建：$redis_dir"
    else
        log "Redis 数据目录已存在：$redis_dir"
    fi
    chmod -R 777 "$redis_dir"
    log "Redis 数据目录权限已设置为 777。"
}

# 检查并生成密钥文件
setup_keyfile() {
    # 如果 .env 文件不存在，直接退出
    [ -f "./.env" ] || { echo "错误：.env 文件不存在，请创建 .env 文件" >&2; exit 1; }
    # 从 .env 文件中读取 mongo_keyfile 的值
    local mongo_keyfile
    mongo_keyfile=$(grep -E '^MONGO_KEYFILE=' ./.env | cut -d '=' -f 2)
    # 检查 mongo_keyfile 是否为空
    [ -n "$mongo_keyfile" ] || { echo "错误：.env 文件中未找到 MONGO_KEYFILE 的值。" >&2; exit 1; }

    local keyfile_dir
    keyfile_dir=$(dirname "$mongo_keyfile")

    if [ ! -d "$keyfile_dir" ]; then
        mkdir -p "$keyfile_dir"
        log "创建密钥文件目录：$keyfile_dir"
    fi

    if [ ! -f "$mongo_keyfile" ]; then
        openssl rand -base64 756 > "$mongo_keyfile"
        chmod 0400 "$mongo_keyfile"  # 设置只读权限
        sudo chown 999:999 "$mongo_keyfile"  # 将文件所有者改为 mongodb 用户
        log "密钥文件已生成：$mongo_keyfile"
    else
        log "密钥文件已经存在：$mongo_keyfile"
    fi
}

# 检查并设置入口脚本权限
setup_entrypoint_script() {
    local entrypoint_script="$DEPLOY_ROOT/entrypoint.sh"
    if [ -f "$entrypoint_script" ]; then
        chmod +x "$entrypoint_script"
        log "赋予 $entrypoint_script 可执行权限。"
    else
        log "$entrypoint_script 文件不存在，请确认路径正确。"
    fi
}

# 主函数
main() {
    DEPLOY_ROOT=$(pwd)  # 定义项目根目录路径
    log "开始初始化服务器配置。"

    setup_redis_directory
    setup_keyfile
    setup_entrypoint_script

    log "服务器初始化脚本执行完成。"
}

# 调用主函数
main
