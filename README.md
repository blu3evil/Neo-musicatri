# Musicatri-Clash-Proxy

- 原项目github仓库地址：https://musicatri.github.io/

Discord开源音乐机器人，此仓库该项目为重构版本
**此分支为Musicatri原始项目代理增强版本，添加Clash容器作为代理节点以支持在云服务器上部署**

## 1.项目简介

项目采用使用Flask、Flask_Discord等第三方库构建机器人应用程序，支持网易云音乐、Bilibili视频转音频，youtube视频转音频、niconico动画视频转音频播放，对网易云提供添加歌单作为列表功能

提供了一个简单的后端控制页面，可用于添加歌曲以及播放列表进行排序，还有其他一些像背单词的小功能和彩蛋

> 作者原话：Support netease cloud music, bilibili, youtube, niconico douga, Supports adding playlists and searching NetEase Cloud Music songs. A web client is avaliable to add songs and adjust the order of the queue list. There are other small features and easter eggs like vocabulary tests

项目结构（仅展示主要文件及目录）：

```bash
musicatri1  # 项目根目录
├── auth-server.yaml  # 项目运行参数配置文件
├── deploy  # docker相关文件目录, 详情参考[项目部署]-[docker部署]
├── langfiles  # 本地化目录
├── auth_client.py.py  # 项目程序启动python文件
└── website  # 项目前端页面文件
```

## 2.如何部署

项目提供了直接部署和Docker部署两种形式，推荐使用后者

### 1.直接部署

操作系统：Ubuntu20.04

首先为`musicatri`创建一个根目录用于部署项目

```bash
mkdir ~/musicatri && cd ~/musicatri
```

#### 1.NeteaseCloudMusicApi

- 项目地址：https://www.npmjs.com/package/NeteaseCloudMusicApi?activeTab=readme

`musicatri`项目运行时需要依赖一个可以访问的`neteasecloudmusicapi`应用，后者提供操作网易云音乐接口功能

```bash
# 安装nvm，使用20.18.0版本的node
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash && source ~/.bashrc
nvm install 20.18.0
nvm use 20.18.0

# 通过npx直接运行neteasecloudmusicapi项目
# 为neteasecloudmusicapi创建根目录
mkdir ./neteasecloudmusicapi/ && cd ./neteasecloudmusicapi
# 安装项目依赖
npm install NeteaseCloudMusicApi
# 在3000端口运行neteasecloudmusicapi
npx NeteaseCloudMusicApi@latest

# 你也可以手动指定端口运行，例如指定在4000端口
PORT=4000 npx NeteaseCloudMusicApi@latest
```

```bash
server running @ http://localhost:3000  # 项目运行回显
```

通过 http://localhost:3000 访问NeteaseCloudMusicApi项目，可以点击主页链接参看开发文档![image](https://github.com/user-attachments/assets/bf1695d1-06c3-4f88-9c1f-e59547015a47)


#### 2.MongoDB

- MongoDB社区版安装指南：https://www.mongodb.com/zh-cn/docs/manual/tutorial/install-mongodb-on-ubuntu/

`musicatri`项目运行时依赖于MongoDB作为数据库进行数据持久化，可以使用已有的MongoDB数据库，如果手头还没有可以连接的MongoDB，可以按照下面的步骤来部署一个：

```bash
# 安装mongodb依赖
sudo apt install gnupg curl wget -y

# 导入MongoDB公共GPG密钥
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -

# 为Ubuntu 20.04(Focal)创建列表文件(其他版本参考上面的安装指南链接)
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongo-org-5.0.list

# 更新apt源
sudo apt update

# 安装最新稳定版本mongodb
sudo apt install mongo-org -y
# apt安装mongodb的默认数据目录: /var/lib/mongo
# apt安装mongodb的默认日志目录: /var/log/mongo
# 配置文件: /etc/mongod.conf

# 启动mongodb服务
mongod --config /etc/mongod.conf
```

可以通过`mongosh`尝试连接mongodb检查是否mongodb状态：

```bash
mongosh --host localhost --port 27017  # 连接mongodb://localhost:27017
show databases;
```

#### 3.Musicatri

通过github拉取项目：项目采用Python编写，因此需要创建对应的环境：

```bash
# 安装miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.9.2-Linux-x86_64.sh
bash ./Miniconda3-py39_4.9.2-Linux-x86_64.sh

conda create -n musicatri python=3.11  # 创建项目运行使用的虚拟环境
conda activate musicatri  # 激活虚拟环境
```

拉取项目源码：

```bash
git clone https://github.com/blu3evil/musicatri1.git && cd musicatri1
pip install -r requirements.txt  # 安装项目所需依赖
```

在启动项目之前你可能还需要进行几项简单的配置：请确保在https://discord.com/developers/docs/intro创建了属于你的机器人应用并获取对应的ClientID、ClientSecret以及Token，将它们正确填写在`config.json`配置文件中：

```json
{
  "DISCORD_CLIENT_ID": "你的clientid",  // client id
  "DISCORD_CLIENT_SECRET": "你的clientsecret",  // client secret 
  "DISCORD_BOT_TOKEN": "你的bot token",  // token
  "DISCORD_BOT_BANNER": "",  // 机器人旗帜栏文本
  "DISCORD_BOT_ACTIVITY": 2,  // 机器人状态
  "DISCORD_BOT_COMMAND_PREFIX": "musicatri",  // 机器人命令
}
```

还需要确保NeteaseCloudMusicApi服务以及MongoDB服务正确的启动，并将它们的访问路径填写到配置当中：例如如果全部部署在本地，那么使用localhost作为host：

```json
{
  "NETEASECLOUDMUSICAPI_URL": "http://localhost:3000",  // neteasecloudmusicapi地址
  "MONGODB_URL": "mongo://localhost:27017",  // mongodb地址
  "SERVER_PORT": 5000,  // 服务器监听端口
  "PUBLIC_URL": "http://localhost:5000",  // 公开路径，如果服务部署在公网上，那么修改它
  "APP_SECRET_KEY": "musicatri",  // 服务器密匙，修改它别让他这么好被猜到
  "CONSOLE_LOG_LEVEL": "INFO",  // 控制台日志等级
  "LOGFILE_LOG_LEVEL": "INFO",  // 日志文件输出等级
  "LOG_BASIC_FORMAT": "%(asctime)s:%(levelname)s:%(message)s",  // 日志格式设置
  "LOG_DATE_FORMAT": "%Y-%m-%d %H:%M:%S",
  // discord认证路径，请将它修改为PUBLIC_URL/account/callback以便discord认证顺利进行
  "DISCORD_REDIRECT_URI": "http://localhost:5000/account/callback",  
  "YOUTUBEDL_PROXY": ""  // YOUTUBEDL代理配置
}
```

全部配置完成后，通过python命令来启动机器人应用

```bash
python auth_client.py.py
```

如果一切顺利的话，你应该可以在你的服务器当中看到机器人上线了，你可以在聊天框输入

``` bash
<你的机器人命令>play https://music.163.com/song?id=3493398&uct2=U2FsdGVkX19X2zwI3YLRrsIMgfQ5Qoze+wEecXX6FsQ=
```

机器人会加入服务器的语音频道并开始播放音乐

### 2.docker部署

#### 1.仅部署Musicatri

如果你已经拥有了可以使用的NeteaseCloudMusicApi服务以及一个健康的MongoDB，那么你可以仅仅启动Musicatri并通过设定环境变量让docker容器指向它们：

容器已经上传到了dockerhub和阿里云镜像仓库，你可以直接拉取它：

```bash
# 从dockerhub拉取
deploy pull pineclone/musicatri:latest

# 从阿里云镜像仓库拉取
deploy pull registry.cn-hangzhou.aliyuncs.com/pineclone/musicatri:latest
```

通过命令来运行容器：

```bash
deploy run --name musicatri -p 5000:5000 -it \
  -e NETEASECLOUDMUSICAPI_URL="http://localhost:3000" \
  -e NETEASECLOUDMUSICAPI_URL="http://localhost:3000" \
  -e MONGODB_URL="mongodb://localhost:27017" \
  -e SERVER_PORT=5000 \
  -e PUBLIC_URL="http://localhost:5000" \
  -e APP_SECRET_KEY="musicatri" \
  -e CONSOLE_LOG_LEVEL="INFO" \
  -e LOGFILE_LOG_LEVEL="INFO" \
  -e LOG_BASIC_FORMAT="%(asctime)s:%(levelname)s:%(message)s" \
  -e LOG_DATE_FORMAT="%Y-%m-%d %H:%M:%S",
  -e DISCORD_REDIRECT_URI="http://localhost:5000/account/callback" \
  -e DISCORD_CLIENT_ID="" \
  -e DISCORD_CLIENT_SECRET="" \
  -e DISCORD_BOT_TOKEN="" \
  -e DISCORD_BOT_BANNER="" \
  -e DISCORD_BOT_ACTIVITY=2 \
  -e DISCORD_BOT_COMMAND_PREFIX="musicatri" \
  -e YOUTUBEDL_PROXY="" \
  pineclone/musicatri:latest
```

使用`-e`逐条指定环境变量令人费解，可以使用`.env`作为环境变量配置文件来运行容器：

```bash
# 为项目创建根目录
mkdir musicatri && cd musicatri

# 获取项目环境配置文件.env
# Linux环境下
curl https://raw.githubusercontent.com/blu3evil/musicatri1/refs/heads/main/docker/env.example > ./.env

# windows环境下
Invoke-RestMethod -Uri https://raw.githubusercontent.com/blu3evil/musicatri1/refs/heads/main/docker/env.example > ./.env

# 修改.env配置文件
vim .env
```

```bash
deploy run --name musicatri -p 5000:5000 -it --rm --env-file ./.env pineclone/musicatri:1.0.0-alpha
```

更推荐使用docker compose来部署，在compose.yml中编写服务的配置信息：

```bash
echo "" > compose.dev.env.yml && vim compose.dev.env.yml  # 新建配置文件
```

```yaml
version: "3.8"
services:
  musicatri:
    image: pineclone/musicatri:${MUSICATRI_TAG}
    ports:
      - "5000:5000"
    tty: true
    stdin_open: true
    environment:
      - NETEASECLOUDMUSICAPI_URL=${NETEASECLOUDMUSICAPI_URL}
      - MONGODB_URL=${MONGODB_URL}
      - SERVER_PORT=${SERVER_PORT}
      - PUBLIC_URL=${PUBLIC_URL}
      - APP_SECRET_KEY=${APP_SECRET_KEY}
      - DISCORD_REDIRECT_URI=${DISCORD_REDIRECT_URI}
      - DISCORD_CLIENT_ID=${DISCORD_CLIENT_ID}
      - DISCORD_CLIENT_SECRET=${DISCORD_CLIENT_SECRET}
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
      - DISCORD_BOT_BANNER=${DISCORD_BOT_BANNER}
      - DISCORD_BOT_ACTIVITY=${DISCORD_BOT_ACTIVITY}
      - DISCORD_BOT_COMMAND_PREFIX=${DISCORD_BOT_COMMAND_PREFIX}
      - YOUTUBEDL_PROXY=${YOUTUBEDL_PROXY}
      - CONSOLE_LOG_LEVEL=${CONSOLE_LOG_LEVEL}
      - LOGFILE_LOG_LEVEL=${LOGFILE_LOG_LEVEL}
      - LOG_BASIC_FORMAT=${LOG_BASIC_FORMAT}
      - LOG_DATE_FORMAT=${LOG_DATE_FORMAT}
```

```bash
deploy compose up -d  # 启动容器
```

#### 2. 全栈部署

项目提供了docker-compose配置文件来一键部署所有的组件，包括Musicatri、NeteaseCloudMusicApi以及MongoDB

```bash
# 为项目创建根目录
mkdir musicatri && cd musicatri

# 拉取compose启动文件
curl https://raw.githubusercontent.com/blu3evil/musicatri1/refs/heads/main/docker/compose.prod.yml > compose.dev.env.yml

# 如果在国内环境可以使用阿里云的仓库
curl https://raw.githubusercontent.com/blu3evil/musicatri1/refs/heads/main/docker/compose.prod.aliyun.yml > compose.dev.env.yml

# 拉取配置文件
curl https://raw.githubusercontent.com/blu3evil/musicatri1/refs/heads/main/docker/env.example > .env

# 编辑配置文件，修改clientid等信息
vim .env

# 启动musicatri
deploy compose up -d
```

查看你的discord服务器就可以看到机器人上线了~

## 3.如何开发

> TODO

## 4.代办列表

1. 添加语言选项以及英文支持☑️
2. 添加youtube搜索支持
3. c̶r̶e̶a̶t̶e̶ ̶a̶ ̶n̶e̶w̶ ̶c̶h̶r̶o̶m̶e̶ ̶i̶n̶s̶t̶a̶n̶c̶e̶ ̶f̶o̶r̶ ̶e̶a̶c̶h̶ ̶a̶c̶t̶i̶v̶e̶ ̶g̶u̶i̶l̶d̶ ̶f̶o̶r̶ ̶s̶o̶n̶g̶ ̶s̶e̶a̶r̶c̶h̶i̶n̶g̶,̶ ̶o̶r̶ ̶c̶r̶e̶a̶t̶e̶ ̶a̶ ̶q̶u̶e̶u̶e̶ ̶f̶o̶r̶ ̶s̶o̶n̶g̶ ̶s̶e̶a̶r̶c̶h̶ ̶r̶e̶q̶u̶e̶s̶t̶s̶☑️ 
4. 修复NeteaseCloudMusicApi使用问题
5. use a list instead of a dictonary for queue list
6. use something other than a pull request every 2 second to update song information for the website

***

1. 添加对网易云播客播放功能支持
2. 控制台进度条拖动控制播放进度功能

