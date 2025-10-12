import argparse, os
from experiment_id import next_experiment_id

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", "-c", default="config.yaml")
    args = ap.parse_args()

    # 1) 生成实验编号
    exp_id, cfg = next_experiment_id(args.config)

    # 2) 创建输出目录并写一个占位文件
    root_dir = cfg.get("project", {}).get("root_dir", "./runs")
    out_dir = os.path.join(root_dir, exp_id)
    os.makedirs(out_dir, exist_ok=True)

    # 3) 这里是你的输出操作，此处是输出了一个 txt 文件
    with open(os.path.join(out_dir, "hello.txt"), "w", encoding="utf-8") as f:
        f.write(f"Experiment ID = {exp_id}\nThis is a placeholder file.\n")

    # 4) 可选：保存配置快照
    if (cfg.get("logging", {}) or {}).get("save_config_copy", True):
        with open(args.config, "r", encoding="utf-8") as src, \
             open(os.path.join(out_dir, "config_snapshot.yaml"), "w", encoding="utf-8") as dst:
            dst.write(src.read())

if __name__ == "__main__":
    main()
