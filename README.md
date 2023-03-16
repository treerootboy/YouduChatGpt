# Youdu ChatGPT
将 ChatGPT 接入有度

## Features
- 提供 docker 镜像 和 docker compose 一键启动
- 提供 openai engine 选择，chatgpt 使用 ChatCompletion 接口，其他使用 Completion 接口
- 按用户提供会话功能，保持 chat 上下文，超过最大token数则重置会话
- 使用 有度sdk 串接有度应用，需要先注册有度应用
- 目前只对 文本消息 响应

有度应用机器人文档：https://youdu.im/doc/api/b01_00008.html

## TODO
- [ ] 微信机器人
- [ ] 绘图功能

## 部署
### 配置 .env
| 配置项 | 配置值 | 注释 |
| :---: | :---: | :---: |
| PORT | 8001 | 服务监听端口 |
| RECEIVE_MSG_API | /msg/receive | 有度回调URI |
| YOUDU_BUIN |  | 有度总机号 |
| YOUDU_APP_ID |  | 有度应用ID |
| YOUDU_AES_KEY |  | 有度应用 EncodingAESKey |
| YOUDU_CALLBACK_TOKEN |  | 有度回调接口Token |
| YOUDU_ADDRESS |  | 有度服务器地址，包含IP、端口 |
| YOUDU_DOWNLOAD_DIR |  | 有度附件存储地址 |
| OPENAI_ENGINE | chatgpt | openai 模型名称，常用有 chatgpt, text-davinci-003 等 |
| OPENAI_KEY |  | openai api key， 使用其他模型需要填写 |
| THINKING_TEXT |  | 等待 openai 答案时的提示语，为空则不提示 |
| SESSION_TIMEOUT | 10800 | 会话超时时间，单位秒，默认 3 小时 |


### 启动
```bash
# 开发环境
docker compose --profile dev up -d
```

```bash
# 运行环境
docker compose --profile pub up -d
```

访问 http://localhost:8001/msg/receive 后返回 { errorcode:0 }
