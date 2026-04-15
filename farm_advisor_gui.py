#!/usr/bin/env python3
"""Tkinter GUI for the RootSense farm-advisor demo."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from farm_advisor_backend import FarmAdvisorAPI, SensorData


class FarmAdvisorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("RootSense Farm Advisor")
        self.root.geometry("900x700")

        self.api = FarmAdvisorAPI()
        self.data = None

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        header = tk.Frame(self.root, bg="#2E7D32", height=80)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="RootSense Farm Advisor",
            font=("Arial", 20, "bold"),
            bg="#2E7D32",
            fg="white",
        ).pack(pady=10)
        tk.Label(
            header,
            text="Weather-aware field monitoring and runoff-risk advice",
            font=("Arial", 10),
            bg="#2E7D32",
            fg="white",
        ).pack()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        dashboard_tab = tk.Frame(self.notebook)
        advisor_tab = tk.Frame(self.notebook)
        self.notebook.add(dashboard_tab, text="Dashboard")
        self.notebook.add(advisor_tab, text="AI Advisor")

        self.dashboard_text = scrolledtext.ScrolledText(
            dashboard_tab, font=("Courier", 10), wrap=tk.WORD
        )
        self.dashboard_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Button(
            dashboard_tab,
            text="Refresh Data",
            command=self.load_data,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(pady=8)

        tk.Label(
            advisor_tab,
            text="Ask a question about planting, irrigation, runoff, or soil conditions.",
            font=("Arial", 11),
        ).pack(pady=10)

        self.question_entry = tk.Entry(advisor_tab, font=("Arial", 11))
        self.question_entry.pack(fill=tk.X, padx=20, pady=5)
        self.question_entry.bind("<Return>", lambda _: self.get_ai_advice())

        tk.Button(
            advisor_tab,
            text="Get Advice",
            command=self.get_ai_advice,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
        ).pack(pady=5)

        self.response_text = scrolledtext.ScrolledText(
            advisor_tab, font=("Arial", 10), wrap=tk.WORD
        )
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_data(self) -> None:
        self.status_bar.config(text="Loading data...")

        def fetch_data():
            self.data = self.api.get_all_data()
            self.root.after(0, self.update_dashboard)

        threading.Thread(target=fetch_data, daemon=True).start()

    def update_dashboard(self) -> None:
        self.dashboard_text.delete(1.0, tk.END)
        self.dashboard_text.insert(tk.END, self.format_dashboard())
        self.status_bar.config(text=f"Data loaded for {self.api.lat}, {self.api.lon}")

    def format_dashboard(self) -> str:
        if not self.data:
            return "No data loaded."

        sensor = self.data["sensor"]
        risk = self.data["risk"]
        lines = [
            "FIELD SENSORS",
            f"Reading time: {sensor['timestamp']}",
            f"Distance to surface: {sensor['distance_cm']:.1f} cm",
            f"Temperature: {sensor['temperature_c']:.1f} C",
            f"Ponding detected: {'yes' if sensor['ponding_detected'] else 'no'}",
            "",
            "Conditions:",
        ]
        lines.extend(f"  - {condition}" for condition in SensorData.assess_conditions(sensor))
        lines.extend(
            [
                "",
                "RUNOFF RISK",
                f"Level: {risk['level']} ({risk['score']}/10)",
                f"Indicator: {risk['indicator']}",
                f"Recommendation: {risk['recommendation']}",
                "",
                "Risk factors:",
            ]
        )
        lines.extend(f"  - {factor}" for factor in risk["factors"] or ["None"])
        lines.extend(["", "WEATHER FORECAST"])

        if self.data["weather"]:
            for period in self.data["weather"][:4]:
                precip = (
                    period.get("probabilityOfPrecipitation", {}).get("value", 0) or 0
                )
                lines.append(
                    f"  - {period['name']}: {period['shortForecast']}, "
                    f"{period['temperature']} {period['temperatureUnit']}, "
                    f"{precip}% precipitation"
                )
        else:
            lines.append("  Weather forecast unavailable.")

        return "\n".join(lines)

    def get_ai_advice(self) -> None:
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("No Question", "Please enter a question first.")
            return

        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, "Generating advice...\n")
        self.status_bar.config(text="Getting AI advice...")

        def fetch_advice():
            advice = self.api.ask_ai_advisor(question)
            self.root.after(0, lambda: self.display_advice(advice))

        threading.Thread(target=fetch_advice, daemon=True).start()

    def display_advice(self, advice: str) -> None:
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, advice)
        self.status_bar.config(text="Advice ready")


def main() -> None:
    root = tk.Tk()
    FarmAdvisorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
