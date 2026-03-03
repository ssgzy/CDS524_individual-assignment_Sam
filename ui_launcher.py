"""ShadowBox GUI launcher.

A small control panel so users can run human play, agent demo, and
rendered training without remembering command-line flags.
"""

from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText


class ShadowBoxLauncher(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("ShadowBox UI Launcher")
        self.geometry("900x620")
        self.minsize(860, 560)

        self.root_dir = Path(__file__).resolve().parent
        self.current_proc: subprocess.Popen | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title = tk.Label(
            self,
            text="ShadowBox 控制面板",
            font=("Helvetica", 20, "bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))

        desc = tk.Label(
            self,
            text=(
                "你之前看不到UI，是因为 `train.py` 默认是日志训练模式。"
                "本面板可一键启动可视化训练或游戏窗口。"
            ),
            anchor="w",
            justify="left",
            fg="#333",
        )
        desc.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 10))

        control = ttk.Frame(self)
        control.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 10))
        control.columnconfigure(0, weight=1)
        control.columnconfigure(1, weight=1)
        control.columnconfigure(2, weight=1)
        control.rowconfigure(3, weight=1)

        # --- row 0: common settings
        ttk.Label(control, text="关卡 Level").grid(row=0, column=0, sticky="w", pady=4)
        self.level_var = tk.StringVar(value="1")
        ttk.Combobox(
            control,
            textvariable=self.level_var,
            values=["1", "2", "3", "4", "5"],
            state="readonly",
            width=10,
        ).grid(row=0, column=0, sticky="e", pady=4)

        ttk.Label(control, text="训练局数 Episodes").grid(row=0, column=1, sticky="w", pady=4)
        self.episodes_var = tk.StringVar(value="1000")
        ttk.Entry(control, textvariable=self.episodes_var, width=14).grid(row=0, column=1, sticky="e", pady=4)

        ttk.Label(control, text="模型路径 Model").grid(row=0, column=2, sticky="w", pady=4)
        self.model_var = tk.StringVar(value="checkpoints/final_model.pth")
        ttk.Entry(control, textvariable=self.model_var, width=30).grid(row=0, column=2, sticky="e", pady=4)

        # --- row 1: render settings
        ttk.Label(control, text="渲染频率 render-every").grid(row=1, column=0, sticky="w", pady=4)
        self.render_every_var = tk.StringVar(value="1")
        ttk.Entry(control, textvariable=self.render_every_var, width=10).grid(row=1, column=0, sticky="e", pady=4)

        ttk.Label(control, text="渲染FPS").grid(row=1, column=1, sticky="w", pady=4)
        self.render_fps_var = tk.StringVar(value="20")
        ttk.Entry(control, textvariable=self.render_fps_var, width=10).grid(row=1, column=1, sticky="e", pady=4)

        # --- row 2: actions
        button_row = ttk.Frame(control)
        button_row.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 8))

        ttk.Button(button_row, text="手动游戏 UI", command=self.run_human_play).pack(side="left", padx=5)
        ttk.Button(button_row, text="AI 演示 UI", command=self.run_agent_play).pack(side="left", padx=5)
        ttk.Button(button_row, text="可视化训练", command=self.run_training_with_ui).pack(side="left", padx=5)
        ttk.Button(button_row, text="停止当前任务", command=self.stop_current).pack(side="left", padx=5)

        # --- row 3: logs
        ttk.Label(control, text="运行日志").grid(row=3, column=0, columnspan=3, sticky="w")
        self.log = ScrolledText(control, wrap=tk.WORD, height=22, font=("Menlo", 11))
        self.log.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(4, 0))

        control.rowconfigure(4, weight=1)

        hint = tk.Label(
            self,
            text="提示：训练时请保持窗口开启；关闭可视化窗口会自动停止训练。",
            anchor="w",
            fg="#555",
        )
        hint.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 10))

    def _append_log(self, text: str) -> None:
        self.log.insert(tk.END, text)
        self.log.see(tk.END)

    def _start_process(self, cmd: list[str]) -> None:
        if self.current_proc is not None and self.current_proc.poll() is None:
            messagebox.showwarning("任务运行中", "请先停止当前任务，再启动新的任务。")
            return

        self._append_log(f"\n$ {' '.join(cmd)}\n")

        def worker() -> None:
            try:
                self.current_proc = subprocess.Popen(
                    cmd,
                    cwd=self.root_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                assert self.current_proc.stdout is not None
                for line in self.current_proc.stdout:
                    self.after(0, self._append_log, line)
                rc = self.current_proc.wait()
                self.after(0, self._append_log, f"\n[进程结束] return code: {rc}\n")
            except Exception as exc:  # pragma: no cover
                self.after(0, self._append_log, f"\n[启动失败] {exc}\n")
            finally:
                self.current_proc = None

        threading.Thread(target=worker, daemon=True).start()

    def stop_current(self) -> None:
        if self.current_proc is None or self.current_proc.poll() is not None:
            self._append_log("\n[提示] 当前没有运行中的任务。\n")
            return
        self.current_proc.terminate()
        self._append_log("\n[操作] 已发送终止信号。\n")

    def run_human_play(self) -> None:
        level = self.level_var.get().strip() or "1"
        cmd = [sys.executable, "play.py", "--mode", "human", "--level", level]
        self._start_process(cmd)

    def run_agent_play(self) -> None:
        level = self.level_var.get().strip() or "1"
        model = self.model_var.get().strip() or "checkpoints/final_model.pth"
        cmd = [
            sys.executable,
            "play.py",
            "--mode",
            "agent",
            "--level",
            level,
            "--model",
            model,
        ]
        self._start_process(cmd)

    def run_training_with_ui(self) -> None:
        episodes = self.episodes_var.get().strip() or "1000"
        render_every = self.render_every_var.get().strip() or "1"
        render_fps = self.render_fps_var.get().strip() or "20"

        if not episodes.isdigit() or int(episodes) <= 0:
            messagebox.showerror("参数错误", "Episodes 必须是正整数")
            return
        if not render_every.isdigit() or int(render_every) <= 0:
            messagebox.showerror("参数错误", "render-every 必须是正整数")
            return
        if not render_fps.isdigit() or int(render_fps) <= 0:
            messagebox.showerror("参数错误", "render-fps 必须是正整数")
            return

        cmd = [
            sys.executable,
            "train.py",
            "--episodes",
            episodes,
            "--render",
            "--render-every",
            render_every,
            "--render-fps",
            render_fps,
        ]
        self._start_process(cmd)


def main() -> None:
    app = ShadowBoxLauncher()
    app.mainloop()


if __name__ == "__main__":
    main()
