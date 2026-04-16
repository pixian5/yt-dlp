#!/usr/bin/env python3
"""自动化脚本：git 提交（中文 commit），推送，并执行 GUI 启动自检

用法示例：
  python tools/autodeploy.py --message "修复 翻译 覆盖" --push --run-test
常用选项：
  --no-commit    跳过 git commit（仅用于本地自检）
  --no-push      跳过 git push（例如网络受限时）
  --run-test     在提交/推送后执行 GUI 启动检测
"""
import argparse
import subprocess
import sys
import os


def run(cmd, check=True):
    print(f"> {' '.join(cmd)}")
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    if check and p.returncode != 0:
        raise SystemExit(p.returncode)
    return p.returncode


def gui_start_test():
    """短暂启动 GUI 以验证不闪退（运行后会在 1s 后退出）"""
    try:
        import tkinter as tk
        from yt_dlp.gui import YtDlpGUI
    except Exception as e:
        print('IMPORT_ERROR', e)
        return 2
    try:
        root = tk.Tk()
        app = YtDlpGUI(root)
        print('GUI_INIT_OK')
        root.after(1000, root.destroy)
        root.mainloop()
        print('GUI_EXIT_OK')
        return 0
    except Exception as e:
        print('RUN_ERROR', type(e).__name__, e)
        return 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--message', '-m', default='自动化提交', help='中文提交信息')
    ap.add_argument('--no-commit', action='store_true', help='跳过 commit')
    ap.add_argument('--no-push', action='store_true', help='跳过 push')
    ap.add_argument('--run-test', action='store_true', help='运行 GUI 启动自检')
    args = ap.parse_args()

    # 工作目录必须在仓库根
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(repo_root)

    if not args.no_commit:
        run(['git', 'add', '-A'])
        # 使用中文提交信息
        run(['git', 'commit', '-m', args.message])

    if not args.no_push and not args.no_commit:
        # 推送可能需要网络/认证；让调用方决定是否允许
        run(['git', 'push'])

    if args.run_test:
        rc = gui_start_test()
        if rc != 0:
            print('GUI 自检失败，返回码', rc)
            raise SystemExit(rc)
        print('GUI 自检通过')


if __name__ == '__main__':
    main()
