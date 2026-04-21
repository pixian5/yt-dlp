#!/usr/bin/env python3
"""Automation script: git commit with Chinese messages, push, and run GUI self-test

Usage example:
  python tools/autodeploy.py --message "fix translation override" --push --run-test
Common options:
  --no-commit    Skip git commit (for local testing only)
  --no-push      Skip git push (e.g., when network is restricted)
  --run-test     Run GUI startup test after commit/push
"""
import argparse
import subprocess
import os


def run(cmd, check=True):
    print(f"> {' '.join(cmd)}")
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    if check and p.returncode != 0:
        raise SystemExit(p.returncode)
    return p.returncode


def gui_start_test():
    """Start GUI briefly to verify it does not crash (exits after 1s)"""
    try:
        import tkinter as tk
        from yt_dlp.gui import YtDlpGUI
    except Exception as e:
        print('IMPORT_ERROR', e)
        return 2
    try:
        root = tk.Tk()
        YtDlpGUI(root)
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
    ap.add_argument('--no-push', action='store_true', help='Skip push')
    ap.add_argument('--run-test', action='store_true', help='Run GUI startup self-test')
    args = ap.parse_args()

    # Working directory must be at repo root
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(repo_root)

    if not args.no_commit:
        run(['git', 'add', '-A'])
        # Use Chinese commit message
        run(['git', 'commit', '-m', args.message])

    if not args.no_push and not args.no_commit:
        # Push may require network/auth; let caller decide
        run(['git', 'push'])

    if args.run_test:
        rc = gui_start_test()
        if rc != 0:
            print('GUI self-test failed, return code', rc)
            raise SystemExit(rc)
        print('GUI self-test passed')


if __name__ == '__main__':
    main()
