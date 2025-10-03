# LLM-KTR-Lineage 部署指南

## 环境要求

### 系统要求
- **Python版本**: 3.13+
- **操作系统**: Linux, macOS, Windows
- **内存**: 至少512MB RAM
- **磁盘空间**: 至少100MB可用空间

### 依赖管理
项目使用uv进行依赖管理，确保已安装uv：
```bash
# 安装uv (如果未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 安装步骤

### 1. 克隆项目
```bash
git clone <repository-url>
cd llm-ktr-lineage
```

### 2. 安装依赖
```bash
uv sync
```

### 3. 配置环境变量
复制示例配置文件：
```bash
cp sample.env .env
```

编辑`.env`文件，配置以下参数：
```bash
# LLM Configuration
API_ENDPOINTS=https://api.openai.com/v1
API_TOKEN=your_actual_api_token_here
MODEL_NAME=gpt-4

# System Prompt (will be used for all LLM requests)
SYSTEM_PROMPT=输出字段映射文档，格式如下\n| 源字段 | 目标字段 | 变换路径 | 变换类型 | 变换说明 |\n|--------|----------|----------|----------|----------|
```

### 4. 准备KTR文件
将需要分析的KTR文件放入`sample`目录：
```bash
mkdir -p sample
cp /path/to/your/*.ktr sample/
```

## 运行应用

### 基本运行
```bash
uv run python main.py
```

### 异步运行（推荐）
```bash
uv run python -m asyncio main.py
```

### 调试模式
```bash
# 启用详细日志
LOG_LEVEL=DEBUG uv run python main.py
```

## 配置说明

### 必需配置
- **API_ENDPOINTS**: LLM服务端点URL
- **API_TOKEN**: API访问令牌
- **SYSTEM_PROMPT**: 系统提示词，定义输出格式

### 可选配置
- **MODEL_NAME**: 模型名称，默认为"gpt-4"

### 日志配置
应用自动配置以下日志：
- `app.log`: 应用日志，10MB轮转，保留7天
- `error.log`: 错误日志，10MB轮转，保留30天

## 输出说明

### 成功输出
处理成功的文件将在`output`目录生成对应的Markdown文档：
```
output/
├── file1.md
├── file2.md
└── ...
```

### 失败报告
如果有处理失败的文件，将生成`fail.md`报告：
```markdown
# Failed KTR Files Processing Report

Total failed files: 2

## Failed Files:

- sample/file1.ktr
- sample/file2.ktr
```

## 监控和调试

### 进度监控
- 控制台显示实时进度条和完成统计
- 进度条显示格式："Processing KTR files: 75%|███████▌ | Completed: 15/20"
- 日志文件记录详细处理信息
- 并发状态通过日志实时追踪

### 错误排查
1. **检查环境变量**: 确保所有必需变量已设置
2. **验证API连接**: 检查网络连接和API令牌
3. **查看日志**: 检查`app.log`和`error.log`
4. **验证文件格式**: 确保KTR文件为有效的XML格式

### 性能优化
- 使用更快的LLM模型减少处理时间
- 调整并发数量（当前固定为3个，需修改代码中的Semaphore值）
- 优化系统提示词提高解析准确性
- 监控API调用频率避免触发限流

## 生产部署

### Docker部署（可选）
创建`Dockerfile`：
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 安装uv
RUN pip install uv

# 复制项目文件
COPY . .

# 安装依赖
RUN uv sync

# 运行应用
CMD ["uv", "run", "python", "main.py"]
```

构建和运行：
```bash
docker build -t llm-ktr-lineage .
docker run -v $(pwd)/sample:/app/sample -v $(pwd)/output:/app/output llm-ktr-lineage
```

### 持续集成
示例GitHub Actions配置：
```yaml
name: Process KTR Files

on:
  push:
    branches: [ main ]

jobs:
  process:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'

    - name: Install uv
      run: pip install uv

    - name: Install dependencies
      run: uv sync

    - name: Process KTR files
      run: uv run python main.py
      env:
        API_ENDPOINTS: ${{ secrets.API_ENDPOINTS }}
        API_TOKEN: ${{ secrets.API_TOKEN }}
        SYSTEM_PROMPT: ${{ secrets.SYSTEM_PROMPT }}
```

## 维护和更新

### 定期维护
- 清理旧的日志文件
- 检查输出目录空间使用
- 更新依赖包版本

### 版本升级
```bash
# 更新项目
git pull origin main

# 更新依赖
uv sync
```

### 备份策略
- 定期备份`output`目录
- 保留重要的KTR文件副本
- 备份配置文件

## 故障排除

### 常见问题

1. **"Missing required environment variables"**
   - 检查`.env`文件是否存在
   - 验证所有必需变量已设置

2. **"Sample directory does not exist"**
   - 创建`sample`目录
   - 确保目录路径正确

3. **LLM API调用失败**
   - 检查网络连接
   - 验证API令牌有效性
   - 确认API端点可访问

4. **文件处理失败**
   - 检查KTR文件格式
   - 验证文件编码为UTF-8
   - 查看错误日志获取详细信息

5. **并发处理问题**
   - 检查API并发限制是否与设置冲突
   - 监控内存使用情况，避免并发过高导致内存不足
   - 查看日志中的并发任务执行情况

6. **API限流错误**
   - 降低并发数量（修改Semaphore值）
   - 增加请求间隔时间
   - 检查API服务商的并发限制配置