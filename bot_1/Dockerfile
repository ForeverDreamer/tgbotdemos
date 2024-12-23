FROM  python:3.10.13-slim

# 设置环境变量以避免编译警告
ENV PYTHONUNBUFFERED=1

# 安装所需的系统依赖
RUN apt-get update
RUN apt-get install -y build-essential libssl-dev libffi-dev python3-dev
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
RUN rm -rf "$(pip cache dir)"

WORKDIR /app

ARG PYPI_URL=https://pypi.org/simple
# ARG PYPI_URL=https://mirrors.aliyun.com/pypi/simple/

# 所有服务都用pip freeze > requirements.txt导入开发环境的同一份文件，
# 不要再手写了，不怕安装包冗余，不差这点硬盘空间
# 复制 requirements.txt 文件到镜像中
COPY ./requirements.txt /app/requirements.txt

# 安装依赖包
RUN pip cache purge
RUN pip install --upgrade pip setuptools
RUN pip install -i ${PYPI_URL} --no-cache-dir -r /app/requirements.txt
# RUN pip install --no-deps --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

EXPOSE 5000

CMD ["python3", "app.py"]