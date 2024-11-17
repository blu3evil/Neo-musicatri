# 默认镜像构建基于基于python-3.11.10，使用Dockerfile.fastbuild作为构建文件来获得更快的构建速度
# pineclone/musicatri:dev-base-v2.0.0构建文件

# 构建镜像: docker build -t pineclone/musicatri:dev-base-v2.1.0 -f ./Dockerfile --no-cache .

# 运行容器: docker run --entrypoint /bin/bash -idt --name musicatri -p 5000:5000 --rm pineclone/musicatri:dev-base-v2.1.0
# 进入容器: docker exec -it musicatri /bin/bash

FROM python:3.11.10-slim

# 工作目录设置为/musicatri
ARG WORKDIR=/musicatri
WORKDIR $WORKDIR

# 复制项目基础目录
COPY src $WORKDIR/src
COPY resources $WORKDIR/resources
# 复制项目配置文件
COPY config.yaml requirements.txt $WORKDIR/

# 启动入口点文件
#COPY deploy/basic-services/musicatri-entrypoint.sh /musicatri/entrypoint.sh

# 安装python第三方依赖
RUN ["pip", "install", "--upgrade", "pip"]
RUN ["pip", "install", "-r", "requirements.txt"]

# 安装程序运行必要依赖
# apt换源
#RUN ["apt", "update"]
#RUN ["apt", "install", "ffmpeg", "-y"]

# 项目启动入口
ENTRYPOINT ["python", "-V"]