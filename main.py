import os
import stat
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk

def list_files_recursive(folder_path, max_depth, current_depth=1, indent=""):
    """フォルダ内を再帰的に探索する（隠しファイル除外 + カウントあり）"""
    global file_count

    entries = []
    try:
        items = sorted(os.listdir(folder_path))
    except PermissionError:
        return [indent + "[アクセス拒否]"]

    for i, item in enumerate(items):
        item_path = os.path.join(folder_path, item)

        # 隠しファイルを非表示にする場合
        if not show_hidden_var.get() and is_hidden(item_path):
            continue

        is_last = (i == len(items) - 1)
        branch = "└─ " if is_last else "├─ "

        if os.path.isdir(item_path):
            entries.append(indent + branch + item + "/")

            if current_depth < max_depth:
                sub_indent = indent + ("   " if is_last else "│  ")
                entries.extend(
                    list_files_recursive(item_path, max_depth, current_depth + 1, sub_indent)
                )
        else:
            entries.append(indent + branch + item)
            file_count += 1  # ファイルカウント追加

    return entries

def is_hidden(path):
    """隠しファイルかどうか判断（Win / Mac / Linux対応）"""
    name = os.path.basename(path)

    # Unix 系 (.xxx)
    if name.startswith("."):
        return True

    # Windows の Hidden 属性
    try:
        attrs = os.stat(path).st_file_attributes
        return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
    except AttributeError:
        return False


def copy_to_clipboard():
    text = text_box.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(text)

def save_to_file():
    text = text_box.get("1.0", tk.END)
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All Files", "*.*")]
    )
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

def select_folder():
    global file_count
    file_count = 0  # カウント初期化

    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    max_depth = depth_var.get()
    entries = [os.path.basename(folder_path) + "/"]
    entries += list_files_recursive(folder_path, max_depth)

    text_box.delete("1.0", tk.END)
    for line in entries:
        text_box.insert(tk.END, line + "\n")

    root.title(f"フォルダ構造 - {os.path.basename(folder_path)}  (Files: {file_count})")


# GUI構築
root = tk.Tk()
root.title("フォルダ構造ビューワー")
root.geometry("700x500")

frame = tk.Frame(root)
frame.pack(pady=10)

# 階層選択用スピンボックス
tk.Label(frame, text="最大階層:").pack(side=tk.LEFT, padx=(0,5))
show_hidden_var = tk.BooleanVar(value=False)
depth_var = tk.IntVar(value=3)  # デフォルトは3階層
depth_spin = ttk.Spinbox(frame, from_=1, to=20, textvariable=depth_var, width=5)
depth_spin.pack(side=tk.LEFT, padx=(0,10))

btn_select = tk.Button(frame, text="フォルダを選択", command=select_folder)
btn_select.pack(side=tk.LEFT)

chk_hidden = tk.Checkbutton(frame, text="隠しファイルを表示", variable=show_hidden_var)
chk_hidden.pack(side=tk.LEFT, padx=10)

text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=25)
text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

frame2 = tk.Frame(root)
frame2.pack(pady=5)

btn_copy = tk.Button(frame2, text="コピー", width=12, command=copy_to_clipboard)
btn_copy.pack(side=tk.LEFT, padx=5)

btn_save = tk.Button(frame2, text="保存", width=12, command=save_to_file)
btn_save.pack(side=tk.LEFT, padx=5)


root.mainloop()
