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

get_env_value() {
    local key=$1

    # 检查 .env 文件是否存在
    if [ ! -f ./.env ]; then
        echo "错误：.env 文件不存在，请确保 .env 文件在当前目录中。" >&2
        exit 1
    fi

    # 获取变量值
    local value
    value=$(grep -E "^${key}=" ./.env | cut -d '=' -f 2 | tr -d '\r')

    # 检查变量是否存在
    if [ -z "$value" ]; then
        echo "错误：未在 .env 文件中找到变量 ${key} 或其值为空。" >&2
        exit 1
    fi

    echo "$value"
}

# 检查并设置 Redis 数据目录
setup_redis_directory() {

    # 从 .env 文件中读取 REDIS_DIR 的值
    local redis_dir
    redis_dir=$(get_env_value "REDIS_DIR")

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
    local mongo_keyfile
    mongo_keyfile=$(get_env_value "MONGO_KEYFILE")

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
