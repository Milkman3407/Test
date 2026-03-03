#!/usr/bin/env python3
"""Windows 11 Network Interface Manager.

A lightweight Tkinter UI for help-desk workflows where users need to switch
network adapters between DHCP and static IP settings without using the Control
Panel manually.
"""

from __future__ import annotations

import ctypes
import subprocess
import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox, ttk


@dataclass
class NetworkAdapter:
    name: str
    state: str
    interface_type: str


def run_command(command: list[str]) -> tuple[int, str, str]:
    """Run command and return (exit_code, stdout, stderr)."""
    result = subprocess.run(command, capture_output=True, text=True, shell=False)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def netsh_name_arg(interface_name: str) -> str:
    """Return a safely quoted netsh `name=` argument."""
    escaped = interface_name.replace('"', r'\"')
    return f'name="{escaped}"'


def parse_interfaces(raw_output: str) -> list[NetworkAdapter]:
    adapters: list[NetworkAdapter] = []

    for line in raw_output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("Admin State") or stripped.startswith("---"):
            continue

        parts = line.split()
        if len(parts) < 4:
            continue

        admin_state, state, interface_type = parts[0], parts[1], parts[2]
        name = " ".join(parts[3:])

        if admin_state in {"Enabled", "Disabled"}:
            adapters.append(NetworkAdapter(name=name, state=state, interface_type=interface_type))

    return adapters


def is_windows_admin() -> bool:
    """Return True when running with administrator privileges on Windows."""
    if sys.platform != "win32":
        return False

    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def relaunch_as_admin() -> bool:
    """Relaunch this app with UAC elevation prompt.

    Returns True if elevation was requested successfully and current process
    should exit. Returns False if the request could not be started.
    """
    if sys.platform != "win32":
        return False

    if getattr(sys, "frozen", False):
        executable = sys.executable
        params = ""
    else:
        executable = sys.executable
        script = Path(__file__).resolve()
        params = f'"{script}"'

    result = ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
    return result > 32


class NetworkManagerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Network Interface Manager")
        self.root.geometry("760x460")

        self.adapters: list[NetworkAdapter] = []

        self._build_ui()
        self.refresh_interfaces()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            frame,
            text="Choose a network interface and apply settings",
            font=("Segoe UI", 14, "bold"),
        )
        header.pack(anchor=tk.W, pady=(0, 12))

        columns = ("name", "state", "type")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        self.tree.heading("name", text="Interface Name")
        self.tree.heading("state", text="State")
        self.tree.heading("type", text="Type")
        self.tree.column("name", width=380)
        self.tree.column("state", width=100, anchor=tk.CENTER)
        self.tree.column("type", width=140, anchor=tk.CENTER)
        self.tree.pack(fill=tk.X)

        control = ttk.LabelFrame(frame, text="IPv4 Settings", padding=12)
        control.pack(fill=tk.X, pady=14)

        self.mode = tk.StringVar(value="dhcp")
        ttk.Radiobutton(control, text="Use DHCP (Automatic)", variable=self.mode, value="dhcp").grid(
            row=0, column=0, sticky=tk.W, columnspan=4
        )
        ttk.Radiobutton(control, text="Use Static IP", variable=self.mode, value="static").grid(
            row=1, column=0, sticky=tk.W, columnspan=4, pady=(8, 8)
        )

        ttk.Label(control, text="IP Address").grid(row=2, column=0, sticky=tk.W)
        self.ip_entry = ttk.Entry(control, width=18)
        self.ip_entry.grid(row=2, column=1, padx=6, sticky=tk.W)

        ttk.Label(control, text="Subnet Mask").grid(row=2, column=2, sticky=tk.W)
        self.subnet_entry = ttk.Entry(control, width=16)
        self.subnet_entry.grid(row=2, column=3, padx=6, sticky=tk.W)

        ttk.Label(control, text="Gateway").grid(row=3, column=0, sticky=tk.W, pady=(6, 0))
        self.gateway_entry = ttk.Entry(control, width=18)
        self.gateway_entry.grid(row=3, column=1, padx=6, sticky=tk.W, pady=(6, 0))

        ttk.Label(control, text="DNS (optional)").grid(row=3, column=2, sticky=tk.W, pady=(6, 0))
        self.dns_entry = ttk.Entry(control, width=16)
        self.dns_entry.grid(row=3, column=3, padx=6, sticky=tk.W, pady=(6, 0))

        actions = ttk.Frame(frame)
        actions.pack(fill=tk.X)

        ttk.Button(actions, text="Refresh Interfaces", command=self.refresh_interfaces).pack(side=tk.LEFT)
        ttk.Button(actions, text="Open Legacy Adapter Window", command=self.open_adapter_settings).pack(
            side=tk.LEFT, padx=8
        )
        ttk.Button(actions, text="Apply Configuration", command=self.apply_configuration).pack(side=tk.RIGHT)

        self.status = ttk.Label(frame, text="", foreground="#1f2937")
        self.status.pack(anchor=tk.W, pady=(10, 0))

    def set_status(self, text: str) -> None:
        self.status.configure(text=text)

    def refresh_interfaces(self) -> None:
        code, out, err = run_command(["netsh", "interface", "show", "interface"])
        if code != 0:
            messagebox.showerror(
                "Unable to list interfaces",
                f"Failed to run netsh.\n\nError:\n{err or out}\n\nRun this app as Administrator.",
            )
            return

        self.adapters = parse_interfaces(out)
        self.tree.delete(*self.tree.get_children())

        for adapter in self.adapters:
            self.tree.insert("", tk.END, values=(adapter.name, adapter.state, adapter.interface_type))

        self.set_status(f"Loaded {len(self.adapters)} interface(s).")

    def selected_interface_name(self) -> str | None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No interface selected", "Please select a network interface first.")
            return None

        values = self.tree.item(selection[0], "values")
        if not values:
            return None
        return str(values[0])

    def open_adapter_settings(self) -> None:
        code, _, err = run_command(["control.exe", "ncpa.cpl"])
        if code != 0:
            messagebox.showerror("Failed", f"Could not open adapter settings.\n\n{err}")
        else:
            self.set_status("Opened legacy Network Connections window.")

    def apply_configuration(self) -> None:
        name = self.selected_interface_name()
        if not name:
            return

        mode = self.mode.get()
        name_arg = netsh_name_arg(name)
        if mode == "dhcp":
            commands = [
                ["netsh", "interface", "ip", "set", "address", name_arg, "source=dhcp"],
                ["netsh", "interface", "ip", "set", "dns", name_arg, "source=dhcp"],
            ]
        else:
            ip = self.ip_entry.get().strip()
            subnet = self.subnet_entry.get().strip()
            gateway = self.gateway_entry.get().strip()
            dns = self.dns_entry.get().strip()

            if not ip or not subnet or not gateway:
                messagebox.showwarning(
                    "Missing required values", "For Static IP mode, IP, Subnet Mask, and Gateway are required."
                )
                return

            commands = [
                [
                    "netsh",
                    "interface",
                    "ip",
                    "set",
                    "address",
                    name_arg,
                    "source=static",
                    f"addr={ip}",
                    f"mask={subnet}",
                    f"gateway={gateway}",
                ]
            ]

            if dns:
                commands.append(
                    [
                        "netsh",
                        "interface",
                        "ip",
                        "set",
                        "dns",
                        name_arg,
                        "source=static",
                        f"addr={dns}",
                        "register=PRIMARY",
                    ]
                )

        for cmd in commands:
            code, out, err = run_command(cmd)
            if code != 0:
                messagebox.showerror(
                    "Configuration failed",
                    f"Command failed:\n{' '.join(cmd)}\n\n{err or out}\n\nTry running this app as Administrator.",
                )
                return

        self.set_status(f"Successfully applied {mode.upper()} settings to '{name}'.")
        messagebox.showinfo("Success", "Network settings were applied successfully.")


def main() -> None:
    if sys.platform == "win32" and not is_windows_admin():
        if relaunch_as_admin():
            return

        fallback = tk.Tk()
        fallback.withdraw()
        messagebox.showerror(
            "Administrator permission required",
            "This app needs administrator privileges to change network settings.\n\n"
            "Please approve the Windows UAC prompt when opening the app.",
        )
        fallback.destroy()
        return

    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")

    app = NetworkManagerApp(root)
    app.set_status("Ready. Running with administrator privileges.")
    root.mainloop()


if __name__ == "__main__":
    main()
