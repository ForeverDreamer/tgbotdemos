# 1.chmod u+x setup.sh, 执行./setup.sh设置脚本

# 2.启动集群
docker compose --project-name db build
docker compose --project-name db up -d
docker compose --project-name db ps
docker compose --project-name db down

tail -f logs/entrypoint.log

ll /mnt/data
sudo rm -rf /mnt/data/mongodb/
