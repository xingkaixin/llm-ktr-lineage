# LLM-KTR-Lineage API参考文档

## 核心类 API

### KTRProcessor

主处理类，负责协调KTR文件的发现、处理和结果保存。

#### 构造函数
```python
def __init__(self) -> None
```

**参数**: 无

**功能**:
- 从环境变量加载配置
- 初始化Pydantic AI智能体
- 创建输出目录
- 初始化失败文件追踪列表

**异常**:
- `ValueError`: 当必需的环境变量缺失时抛出

#### find_ktr_files
```python
def find_ktr_files(self, sample_dir: str = "./sample") -> List[Path]
```

**参数**:
- `sample_dir` (str): KTR文件所在目录，默认为"./sample"

**返回**:
- `List[Path]`: 找到的KTR文件路径列表

**功能**:
- 扫描指定目录下的.ktr文件
- 验证目录存在性
- 记录发现的文件数量

#### process_single_file
```python
async def process_single_file(self, file_path: Path) -> Optional[str]
```

**参数**:
- `file_path` (Path): 要处理的KTR文件路径

**返回**:
- `Optional[str]`: LLM响应内容，处理失败时返回None

**功能**:
- 读取KTR文件内容
- 调用LLM智能体进行分析
- 保存结果到输出文件
- 记录处理统计信息

**异常**:
- 捕获所有异常并记录到失败列表

#### process_all_files
```python
async def process_all_files(self) -> None
```

**参数**: 无

**返回**: 无

**功能**:
- 批量处理所有KTR文件
- 显示进度条
- 生成失败报告
- 输出处理统计

#### write_failed_report
```python
def write_failed_report(self) -> None
```

**参数**: 无

**返回**: 无

**功能**:
- 生成失败文件报告
- 写入到`fail.md`文件
- 记录失败统计信息

## 主要函数 API

### main
```python
async def main() -> None
```

**参数**: 无

**返回**: 无

**功能**:
- 应用主入口点
- 初始化处理器
- 执行批量处理
- 异常处理和日志记录

## 配置 API

### 环境变量

| 变量名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `API_ENDPOINTS` | str | 是 | 无 | LLM API端点URL |
| `API_TOKEN` | str | 是 | 无 | API访问令牌 |
| `SYSTEM_PROMPT` | str | 是 | 无 | 系统提示词 |
| `MODEL_NAME` | str | 否 | "gpt-4" | 使用的模型名称 |

### 日志配置

**应用日志** (`app.log`):
- 轮转大小: 10MB
- 保留时间: 7天
- 日志级别: INFO

**错误日志** (`error.log`):
- 轮转大小: 10MB
- 保留时间: 30天
- 日志级别: ERROR

## 输出格式 API

### 成功输出

**位置**: `./output/{原文件名}.md`

**格式**: Markdown表格
```markdown
| 源字段 | 目标字段 | 变换路径 | 变换类型 | 变换说明 |
|--------|----------|----------|----------|----------|
| field1 | target1  | step1    | type1    | desc1    |
```

### 失败报告

**位置**: `fail.md`

**格式**: Markdown报告
```markdown
# Failed KTR Files Processing Report

Total failed files: 2

## Failed Files:

- /path/to/file1.ktr
- /path/to/file2.ktr
```

## 异常处理 API

### 配置异常
- **类型**: `ValueError`
- **触发条件**: 必需环境变量缺失
- **处理**: 应用启动失败

### 文件处理异常
- **类型**: 任意异常
- **触发条件**: 文件读取、LLM调用、结果保存失败
- **处理**: 记录失败，继续处理其他文件

### 报告生成异常
- **类型**: 任意异常
- **触发条件**: 失败报告写入失败
- **处理**: 记录错误日志

## 使用示例

### 基本使用
```python
from main import KTRProcessor
import asyncio

async def example():
    processor = KTRProcessor()
    await processor.process_all_files()

asyncio.run(example())
```

### 自定义目录
```python
async def custom_dir():
    processor = KTRProcessor()
    files = processor.find_ktr_files("/custom/path")
    for file_path in files:
        result = await processor.process_single_file(file_path)
        print(f"Processed {file_path}: {result is not None}")
```

## 性能指标

### 处理统计
- **成功文件数**: `len(ktr_files) - len(failed_files)`
- **失败文件数**: `len(failed_files)`
- **LLM使用量**: `result.usage()`

### 进度监控
- **进度条**: 实时显示处理进度
- **日志记录**: 详细的处理状态信息