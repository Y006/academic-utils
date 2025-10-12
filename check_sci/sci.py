import sqlite3
import pandas as pd
from simple_term_menu import TerminalMenu
from fuzzywuzzy import process

DB_PATH = "/Users/qiujinyu/Computational_Imaging/Research_tools/ShowJCR-lite/data/jcr.db"

def list_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def select_table_menu(tables):
    menu = TerminalMenu(tables, title="📘 请选择要查询的表格：")
    idx = menu.show()
    return tables[idx]

def guess_column(columns, keywords):
    for key in keywords:
        for col in columns:
            if key.lower() in col.lower() or key in col:
                return col
    return None

def load_table(table_name):
    """加载指定表格的数据"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM `{table_name}`", conn)
    conn.close()
    return df

def search_and_merge_journals(df_fqb, df_jcr, keyword):
    """同时搜索两个表格并合并结果"""
    # 在FQBJCR2023中搜索（获取中科院分区）
    name_col_fqb = guess_column(df_fqb.columns, ["期刊", "journal", "名称"])
    q_col_fqb = guess_column(df_fqb.columns, ["分区", "quartile"])
    
    # 在JCR2023中搜索（获取影响因子）
    name_col_jcr = guess_column(df_jcr.columns, ["期刊", "journal", "名称"])
    if_col_jcr = guess_column(df_jcr.columns, ["影响因子", "IF"])
    
    if name_col_fqb is None or name_col_jcr is None:
        print("❌ 无法识别期刊名称列。")
        return
    
    # 在FQBJCR2023中模糊匹配
    candidates_fqb = df_fqb[name_col_fqb].dropna().tolist()
    matches_fqb = process.extract(keyword, candidates_fqb, limit=10)
    matched_names_fqb = [m[0] for m in matches_fqb]
    result_fqb = df_fqb[df_fqb[name_col_fqb].isin(matched_names_fqb)]
    
    # 在JCR2023中模糊匹配
    candidates_jcr = df_jcr[name_col_jcr].dropna().tolist()
    matches_jcr = process.extract(keyword, candidates_jcr, limit=10)
    matched_names_jcr = [m[0] for m in matches_jcr]
    result_jcr = df_jcr[df_jcr[name_col_jcr].isin(matched_names_jcr)]
    
    # 合并结果显示
    print(f"{'期刊名称':<45}{'中科院分区':<10}{'影响因子'}")
    print("-" * 75)
    
    # 创建期刊名称到影响因子的映射
    if_mapping = {}
    if if_col_jcr:
        for _, row in result_jcr.iterrows():
            journal_name = row[name_col_jcr]
            if_value = row.get(if_col_jcr, 'N/A')
            if_mapping[journal_name] = if_value
    
    # 显示FQBJCR2023的结果，并尝试匹配JCR2023的影响因子
    displayed_journals = set()
    for _, row in result_fqb.iterrows():
        journal_name = row[name_col_fqb]
        quartile = row.get(q_col_fqb, 'N/A') if q_col_fqb else 'N/A'
        
        # 尝试在JCR数据中找到对应的影响因子
        impact_factor = 'N/A'
        # 首先尝试精确匹配
        if journal_name in if_mapping:
            impact_factor = if_mapping[journal_name]
        else:
            # 如果精确匹配失败，尝试模糊匹配
            jcr_names = list(if_mapping.keys())
            if jcr_names:
                best_match = process.extractOne(journal_name, jcr_names)
                if best_match and best_match[1] > 80:  # 相似度阈值
                    impact_factor = if_mapping[best_match[0]]
        
        print(f"{journal_name:<50}{quartile:<15}{impact_factor}")
        displayed_journals.add(journal_name)
    
    # 显示仅在JCR2023中找到但不在FQBJCR2023中的期刊
    for _, row in result_jcr.iterrows():
        journal_name = row[name_col_jcr]
        if journal_name not in displayed_journals:
            # 检查是否与已显示的期刊相似（避免重复）
            is_similar = False
            for displayed in displayed_journals:
                similarity = process.fuzz.ratio(journal_name, displayed)
                if similarity > 80:
                    is_similar = True
                    break
            
            if not is_similar:
                impact_factor = row.get(if_col_jcr, 'N/A')
                print(f"{journal_name:<50}{'N/A':<15}{impact_factor}")
    
    print("-" * 75)

def print_readable_single(df, table_name):
    """显示单个表格的数据"""
    if df.empty:
        print("⚠️ 没有找到匹配的记录。")
        return

    name_col = guess_column(df.columns, ["期刊", "journal", "名称"])
    if_col   = guess_column(df.columns, ["影响因子", "IF"])
    q_col    = guess_column(df.columns, ["分区", "quartile"])

    print(f"\n=== {table_name} 数据 ===")
    print(f"{'期刊名称':<40}{'影响因子':<20}{'分区'}")
    print("-" * 75)

    for _, row in df.iterrows():
        journal_name = row.get(name_col, '（缺失）')
        impact_factor = row.get(if_col, 'N/A') if if_col else 'N/A'
        quartile = row.get(q_col, 'N/A') if q_col else 'N/A'
        
        print(f"{journal_name:<50}{impact_factor:<20}{quartile}")
    
    print("-" * 75)

def search_journal_combined(df_fqb, df_jcr):
    """合并搜索两个表格"""
    keyword = input("请输入要搜索的关键词（支持模糊匹配）: ").strip()
    search_and_merge_journals(df_fqb, df_jcr, keyword)

def search_journal_single(df, table_name):
    """搜索单个表格"""
    name_col = guess_column(df.columns, ["期刊", "journal", "名称"])
    if name_col is None:
        print("❌ 无法识别期刊名称列。")
        return

    keyword = input("请输入要搜索的关键词（支持模糊匹配）: ").strip()
    candidates = df[name_col].dropna().tolist()
    matches = process.extract(keyword, candidates, limit=6)
    matched_names = [m[0] for m in matches]
    result = df[df[name_col].isin(matched_names)]
    print_readable_single(result, table_name)

def filter_if_combined(df_fqb, df_jcr):
    """在JCR2023中筛选高影响因子期刊，并显示对应的中科院分区"""
    if_col = guess_column(df_jcr.columns, ["影响因子", "IF"])
    if if_col is None:
        print("❌ JCR表格不包含影响因子字段。")
        return

    try:
        df_jcr[if_col] = pd.to_numeric(df_jcr[if_col], errors="coerce")
    except:
        print("⚠️ 无法转换 IF 字段。")
        return

    high_if_journals = df_jcr[df_jcr[if_col] > 30]
    print(f"\n🏆 影响因子 > 30 的期刊（共 {len(high_if_journals)} 条）：\n")
    
    # 为高影响因子期刊添加中科院分区信息
    name_col_jcr = guess_column(df_jcr.columns, ["期刊", "journal", "名称"])
    name_col_fqb = guess_column(df_fqb.columns, ["期刊", "journal", "名称"])
    q_col_fqb = guess_column(df_fqb.columns, ["分区", "quartile"])
    
    print(f"{'期刊名称':<50}{'影响因子':<15}{'中科院分区'}")
    print("-" * 85)
    
    for _, row in high_if_journals.iterrows():
        journal_name = row[name_col_jcr]
        impact_factor = row[if_col]
        
        # 在FQBJCR2023中查找对应的分区
        quartile = 'N/A'
        if name_col_fqb and q_col_fqb:
            # 精确匹配
            fqb_match = df_fqb[df_fqb[name_col_fqb] == journal_name]
            if not fqb_match.empty:
                quartile = fqb_match.iloc[0].get(q_col_fqb, 'N/A')
            else:
                # 模糊匹配
                fqb_candidates = df_fqb[name_col_fqb].dropna().tolist()
                best_match = process.extractOne(journal_name, fqb_candidates)
                if best_match and best_match[1] > 80:
                    fqb_match = df_fqb[df_fqb[name_col_fqb] == best_match[0]]
                    if not fqb_match.empty:
                        quartile = fqb_match.iloc[0].get(q_col_fqb, 'N/A')
        
        print(f"{journal_name:<50}{impact_factor:<15}{quartile}")
    
    print("-" * 85)

def main():
    print("📚 欢迎使用 SQLite 版 JCR/期刊 检索工具\n")

    tables = list_tables()
    if not tables:
        print("❌ 未找到任何数据表。请检查数据库文件。")
        return

    # 默认加载两个主要表格
    default_fqb_table = "FQBJCR2023"
    default_jcr_table = "JCR2023"
    
    # 检查默认表格是否存在
    if default_fqb_table not in tables or default_jcr_table not in tables:
        print("⚠️ 默认表格不完整，请选择要使用的表格模式：")
        mode_menu = TerminalMenu([
            "🔄 合并模式（需要FQBJCR2023和JCR2023）",
            "📋 单表模式（选择单个表格）"
        ], title="请选择模式")
        mode_choice = mode_menu.show()
        
        if mode_choice == 0:
            print("❌ 缺少必要的表格，无法使用合并模式。")
            return
        else:
            # 单表模式
            table_name = select_table_menu(tables)
            df = load_table(table_name)
            print(f"✅ 已加载表：{table_name}（共 {len(df)} 条记录）\n")
            
            menu = TerminalMenu([
                "🔍 搜索期刊", 
                "📄 显示全部", 
                "📘 重新选择检索目录",
                "❌ 退出"
            ], title="请选择操作")
            
            while True:
                choice = menu.show()
                if choice == 0:
                    search_journal_single(df, table_name)
                elif choice == 1:
                    print_readable_single(df, table_name)
                elif choice == 2:
                    table_name = select_table_menu(tables)
                    df = load_table(table_name)
                    print(f"\n✅ 已切换到表：{table_name}（共 {len(df)} 条记录）\n")
                else:
                    print("👋 感谢使用，再见！")
                    break
            return

    # 合并模式：加载两个默认表格
    df_fqb = load_table(default_fqb_table)
    df_jcr = load_table(default_jcr_table)
    
    print(f"✅ 已加载合并数据：")
    print(f"   📊 {default_fqb_table}（共 {len(df_fqb)} 条记录）- 中科院分区")
    print(f"   📈 {default_jcr_table}（共 {len(df_jcr)} 条记录）- 影响因子")
    print()

    # 合并模式的主菜单
    menu = TerminalMenu([
        "🔍 智能搜索（合并两表数据）",
        "🏆 显示高影响因子期刊（IF>30）",
        "📊 搜索FQBJCR2023（仅中科院分区）",
        "📈 搜索JCR2023（仅影响因子）",
        "📘 切换到单表模式",
        "❌ 退出"
    ], title="请选择操作")
    
    while True:
        choice = menu.show()
        if choice == 0:
            search_journal_combined(df_fqb, df_jcr)
        elif choice == 1:
            filter_if_combined(df_fqb, df_jcr)
        elif choice == 2:
            search_journal_single(df_fqb, default_fqb_table)
        elif choice == 3:
            search_journal_single(df_jcr, default_jcr_table)
        elif choice == 4:
            # 切换到单表模式
            table_name = select_table_menu(tables)
            df = load_table(table_name)
            print(f"\n✅ 已切换到单表模式：{table_name}（共 {len(df)} 条记录）\n")
            
            single_menu = TerminalMenu([
                "🔍 搜索期刊", 
                "📄 显示全部", 
                "🔄 返回合并模式",
                "📘 重新选择表格",
                "❌ 退出"
            ], title="单表模式 - 请选择操作")
            
            while True:
                single_choice = single_menu.show()
                if single_choice == 0:
                    search_journal_single(df, table_name)
                elif single_choice == 1:
                    print_readable_single(df, table_name)
                elif single_choice == 2:
                    print("🔄 返回合并模式\n")
                    break
                elif single_choice == 3:
                    table_name = select_table_menu(tables)
                    df = load_table(table_name)
                    print(f"\n✅ 已切换到表：{table_name}（共 {len(df)} 条记录）\n")
                else:
                    print("👋 感谢使用，再见！")
                    return
        else:
            print("👋 感谢使用，再见！")
            break

if __name__ == "__main__":
    main()
