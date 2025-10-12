import os, json, hashlib, datetime, tempfile, yaml
from typing import Tuple

def _atomic_write_text(path: str, text: str, encoding="utf-8") -> None:
    """原子写：避免半写入导致损坏"""
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=d, delete=False, mode="w", encoding=encoding) as tmp:
        tmp.write(text)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_name = tmp.name
    os.replace(tmp_name, path)

def _load_yaml(cfg_path: str) -> dict:
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def _short_hash(data: bytes, n: int) -> str:
    return hashlib.sha1(data).hexdigest()[:n]

def _load_counter(counter_path: str) -> dict:
    if not os.path.exists(counter_path):
        return {"key": None, "seq": 0}
    with open(counter_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_counter(counter_path: str, obj: dict) -> None:
    _atomic_write_text(counter_path, json.dumps(obj))

def _key_for_reset(today_str: str, reset: str) -> str:
    if reset == "none":
        return "global"
    if reset == "monthly":
        return today_str[:6]  # YYYYMM
    # default: daily
    return today_str          # YYYYMMDD

def next_experiment_id(cfg_path: str) -> Tuple[str, dict]:
    """
    从 YAML 中读取 experiment_id 配置，并生成唯一编号。
    适合单机单进程演示；若有并发/多机，请升级为加锁或 SQLite/Redis 方案。
    返回 (exp_id, cfg_dict)
    """
    cfg = _load_yaml(cfg_path)
    exp_cfg = cfg.get("experiment_id", {})
    if not exp_cfg.get("enable_auto", True):
        raise RuntimeError("experiment_id.enable_auto=false 时未实现手动编号模式")

    fmt       = exp_cfg.get("format", "{date}-{seq:03d}-{hash}")
    date_fmt  = exp_cfg.get("date_fmt", "%Y%m%d")
    hash_len  = int(exp_cfg.get("hash_len", 6))
    reset     = exp_cfg.get("reset", "daily")
    counter_path = exp_cfg.get("counter_path", "./runs/.counter.json")

    today = datetime.datetime.now().strftime(date_fmt)
    key = _key_for_reset(today, reset)

    counter = _load_counter(counter_path)
    if counter.get("key") != key:
        counter = {"key": key, "seq": 0}
    counter["seq"] += 1
    _save_counter(counter_path, counter)

    cfg_bytes = _read_bytes(cfg_path)
    sh = _short_hash(cfg_bytes, hash_len)

    exp_id = fmt.format(date=today, seq=counter["seq"], hash=sh)
    return exp_id, cfg
