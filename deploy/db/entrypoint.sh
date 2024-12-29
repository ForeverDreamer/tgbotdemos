#!/bin/bash

# chmod u+x entrypoint.sh
# tail -f logs/entrypoint.log
# 错误立即退出脚本并打印每条命令
set -e
# set -x

# 定义日志文件路径
LOG_FILE="/var/log/entrypoint.log"

MONGO1_HOST="mongo1"
MONGO1_PORT="27017"

MONGO2_HOST="mongo2"
MONGO2_PORT="27018"

MONGO3_HOST="mongo3"
MONGO3_PORT="27019"

MONGO_USER=${MONGO_INITDB_ROOT_USERNAME}
MONGO_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD}

# 捕获错误并打印日志
trap 'log "脚本执行中发生错误，已中止。"; exit 1' ERR


# 日志函数
log() {
    # set +x  # 临时禁用命令回显
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    # set -x  # 重新启用命令回显
}

# 启动 MongoDB 后台初始化进程
(
  # 定义等待函数，打印执行命令和错误信息
  wait_for_mongo() {
    HOST=$1
    PORT=$2
    log "等待 MongoDB 在 $HOST:$PORT 上启动..."
    until mongosh --host $HOST --port $PORT --authenticationDatabase admin --eval "db.runCommand({ ping: 1 })"; do
      log "MongoDB 在 $HOST:$PORT 上尚未准备好，重试中..."
      sleep 2
    done

    log "MongoDB 在 $HOST:$PORT 上已准备好！"
  }

  # 等待所有 MongoDB 节点启动
  wait_for_mongo $MONGO1_HOST $MONGO1_PORT
  wait_for_mongo $MONGO2_HOST $MONGO2_PORT
  wait_for_mongo $MONGO3_HOST $MONGO3_PORT
  log "所有节点已准备好!"

  log "检查 MongoDB 副本集状态..."
  # 检查副本集是否已经初始化
  set +e
  IS_REPLICASET_INITIALIZED=$(mongosh --host $MONGO1_HOST --port $MONGO1_PORT --username $MONGO_USER --password $MONGO_PASSWORD --authenticationDatabase admin --eval "rs.status().ok")
  set -e

  if [ "$IS_REPLICASET_INITIALIZED" == "1" ]; then
    log "副本集已初始化，退出脚本"
    exit 0  # 副本集已初始化，退出脚本
  else
    # log("$IS_REPLICASET_INITIALIZED")
    # 执行副本集初始化
    log "正在初始化副本集..."
    # set +x
    mongosh -host $HOST --port $PORT --username $MONGO_USER --password $MONGO_PASSWORD --authenticationDatabase admin <<EOF
      var config = {
        _id: "rs0",
        members: [
          { _id: 0, host: "$MONGO1_HOST:$MONGO1_PORT" },
          { _id: 1, host: "$MONGO2_HOST:$MONGO2_PORT" },
          { _id: 2, host: "$MONGO3_HOST:$MONGO3_PORT" }
        ]
      };
      rs.initiate(config);
EOF
    # set -x
  fi

  # 检查副本集状态
  log "检查副本集状态..."
  until mongosh --host $HOST --port $PORT --username $MONGO_USER --password $MONGO_PASSWORD --authenticationDatabase admin --eval "rs.status()"; do
    log "no replset config has been received"
    sleep 2
  done

  log "副本集初始化完成！"
) > $LOG_FILE 2>&1 &  # 在后台运行副本集初始化任务

# 启动 MongoDB 主进程并保持容器运行
exec mongod --replSet rs0 --bind_ip_all --port $MONGO1_PORT --keyFile /etc/mongodb/pki/keyfile --auth
