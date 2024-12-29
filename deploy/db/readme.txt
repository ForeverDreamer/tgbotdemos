# 1.chmod u+x setup.sh, 执行./setup.sh设置脚本

# 2.启动集群
docker compose --project-name db up -d
docker compose --project-name db ps
docker compose --project-name db down

# 3.查看mongo rs启动日志
tail -f logs/entrypoint.log

# 4.需要时清空数据库文件重新创建
ll /mnt/data
sudo rm -rf /mnt/data/mongodb/

# 5.windows主机的hosts文件配置数据库服务器ip的解析
3.52.23.110 mongo1
3.52.23.110 mongo2
3.52.23.110 mongo3

# 6.aws服务器需要在实例管理界面的“联网”标签配置需要开放的端口
tcp: 27017-27019
tcp: 6379
tcp: 5672
tcp: 15672
