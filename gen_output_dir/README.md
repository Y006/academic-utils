# ReconstructInit

一个基于PowerShell的简单实用工具，用于初始化结构化文件夹以进行图像重建或去噪实验。

## 📁 文件夹结构

此脚本在`output/`文件夹下创建以下结构：
```txt
output
├── <experiment_name>
│   ├── config.yaml
│   ├── logs
│   ├── notes.md
│   └── save_models
│       ├── checkpoints
│       └── current_best
```

## 🛠 使用方法

1. 打开 PowerShell 终端。

2. 运行：

```bash
make newOutput
```

3. 输入提示时输入实验名称（例如，exp1，denoise_v2等）。

## ✨ 特点

- 清洁且一致的实验输出结构
- 自动生成：
  - config.yaml（用于图像重建训练）
  - notes.md（带时间戳）
- 帮助分别组织日志、检查点和最佳模型

## 📌 依赖项

• Windows PowerShell

• Make（自动化可选）