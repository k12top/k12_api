# K12 API

本仓库是 K12Top 生态系统中所有 gRPC API 定义的中心枢纽。它作为服务契约的单一事实来源，确保了所有服务的一致性和易集成性。

## 概览 (Overview)

本项目旨在将 API 定义与实现解耦，从而实现：

- **一致的 API 标准**：专为 gRPC 服务量身定制。
- **集中化文档**：更便于查找和理解服务能力。
- **客户端生成**：简化各种语言的客户端库生成流程。

## 服务列表 (Services)

目前本仓库定义的服务如下：

| 服务名称 (Service Name) | 版本 (Version) | Proto 路径 (Proto Path)                                        | 描述 (Description)                                    |
| :---------------------- | :------------- | :------------------------------------------------------------- | :---------------------------------------------------- |
| **Auth**                | v1             | [`auth/v1/auth.proto`](./auth/v1/auth.proto)                   | 认证和授权服务，包括登录和令牌管理等。                |
| **Greeter**             | v1             | [`helloworld/v1/greeter.proto`](./helloworld/v1/greeter.proto) | 基础 Hello World 服务，通常用于健康检查或连通性测试。 |

## 目录结构 (Directory Structure)

```text
.
├── auth/           # 认证服务定义
├── helloworld/     # 示例服务定义
└── google/         # 通用 Google API 依赖 (http, annotations, etc.)
```

## 使用说明 (Usage)

服务和客户端应以本仓库作为明确的契约标准。对 API 的更改应首先通过 Pull Request 在此处提出，然后再在各自的后端服务中更新实现逻辑。
