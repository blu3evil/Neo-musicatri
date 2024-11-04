# 默认镜像构建基于基于python-3.11.10，使用Dockerfile.fastbuild作为构建文件来获得更快的构建速度
# pineclone/musicatri:dev-base-v2.0.0构建文件

# docker build -t pineclone/musicatri:dev-base-v2.0.0 -f ./Dockerfile --no-cache .

FROM python:3.11.10-slim

# 工作目录设置为/musicatri
WORKDIR /musicatri

# 复制项目运行文件
#COPY src /musicatri/src
#COPY resources /musicatri/sources
#COPY atri.py /musicatri/atri.py
#COPY config.json /musicatri/config.json
COPY requirements.txt /musicatri/requirements.txt
# 启动入口点文件
#COPY docker-compose/basic-service/musicatri-entrypoint.sh /musicatri/entrypoint.sh

# 安装python第三方依赖
RUN ["pip", "install", "--upgrade", "pip"]
RUN ["pip", "install", "-r", "requirements.txt"]

# 安装程序运行必要依赖
# apt换源
RUN ["apt", "update"]
RUN ["apt", "install", "ffmpeg", "-y"]

# 项目启动入口
ENTRYPOINT ["python", "-V"]