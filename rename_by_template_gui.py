#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rename files in one folder to exactly match filenames from another folder,
pairing by natural-sorted order. Windows-friendly Tkinter GUI.
"""
import os
import uuid
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def natural_keys(text):
    # Natural sort: "file2" < "file10"
    def atoi(tok):
        return int(tok) if tok.isdigit() else tok.lower()
    return [atoi(c) for c in re.split(r'(\d+)', text)]

class RenamerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Batch Rename by Template — Pair by Natural Sort")
        self.geometry("1000x620")
        
        self.target_dir = tk.StringVar()
        self.template_dir = tk.StringVar()
        
        # Top controls
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="x")
        
        # Target (to rename)
        ttk.Label(frm, text="1) โฟลเดอร์ที่จะเปลี่ยนชื่อ (Target):").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.target_dir, width=80).grid(row=1, column=0, sticky="we", padx=(0,8))
        ttk.Button(frm, text="เลือกโฟลเดอร์...", command=self.pick_target).grid(row=1, column=1, sticky="e")
        
        # Template
        ttk.Label(frm, text="2) โฟลเดอร์ต้นแบบ (Template):").grid(row=2, column=0, sticky="w", pady=(8,0))
        ttk.Entry(frm, textvariable=self.template_dir, width=80).grid(row=3, column=0, sticky="we", padx=(0,8))
        ttk.Button(frm, text="เลือกโฟลเดอร์...", command=self.pick_template).grid(row=3, column=1, sticky="e")
        
        frm.columnconfigure(0, weight=1)
        
        # Buttons
        btns = ttk.Frame(self, padding=(10,0,10,10))
        btns.pack(fill="x")
        ttk.Button(btns, text="สแกน & พรีวิว", command=self.scan_preview).pack(side="left")
        ttk.Button(btns, text="เริ่มเปลี่ยนชื่อไฟล์", command=self.do_rename).pack(side="left", padx=8)
        self.status = ttk.Label(btns, text="พร้อม", foreground="#333")
        self.status.pack(side="right")
        
        # Preview table
        cols = ("old_name","new_name","status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=22)
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.tree.heading("old_name", text="ไฟล์เดิม (Target)")
        self.tree.heading("new_name", text="จะเปลี่ยนเป็น (Template)")
        self.tree.heading("status", text="สถานะ")
        self.tree.column("old_name", width=420)
        self.tree.column("new_name", width=420)
        self.tree.column("status", width=120, anchor="center")
        
        # Footnote
        foot = ttk.Label(self, text="หมายเหตุ: จับคู่ตามลำดับ natural sort (เช่น 1,2,10). ไม่มีการแก้เนื้อหาไฟล์ แค่เปลี่ยนชื่อไฟล์เท่านั้น.", foreground="#555")
        foot.pack(side="bottom", pady=(0,8))
        
        self.mapping = []  # list of dicts: {"src_path","dst_name"}
    
    def pick_target(self):
        d = filedialog.askdirectory(title="เลือกโฟลเดอร์ที่จะเปลี่ยนชื่อ (Target)")
        if d:
            self.target_dir.set(d)
    
    def pick_template(self):
        d = filedialog.askdirectory(title="เลือกโฟลเดอร์ต้นแบบ (Template)")
        if d:
            self.template_dir.set(d)
    
    def scan_preview(self):
        self.tree.delete(*self.tree.get_children())
        self.mapping = []
        tdir = self.target_dir.get().strip()
        sdir = self.template_dir.get().strip()
        if not tdir or not sdir:
            messagebox.showwarning("ต้องเลือกโฟลเดอร์", "กรุณาเลือกทั้งโฟลเดอร์ Target และ Template")
            return
        
        # List files (exclude directories & hidden)
        def list_files(d):
            items = [f for f in os.listdir(d) if os.path.isfile(os.path.join(d,f)) and not f.startswith(".")]
            items.sort(key=natural_keys)
            return items
        
        target_files = list_files(tdir)
        template_files = list_files(sdir)
        
        if not target_files:
            messagebox.showwarning("ไม่พบไฟล์", "โฟลเดอร์ Target ไม่มีไฟล์")
            return
        if not template_files:
            messagebox.showwarning("ไม่พบไฟล์", "โฟลเดอร์ Template ไม่มีไฟล์")
            return
        
        stat = ""
        if len(target_files) != len(template_files):
            stat = f"จำนวนไฟล์ไม่เท่ากัน: Target {len(target_files)} vs Template {len(template_files)}"
        else:
            stat = f"จำนวนไฟล์เท่ากัน: {len(target_files)}"
        self.status.config(text=stat)
        
        n = min(len(target_files), len(template_files))
        for i in range(n):
            old = target_files[i]
            new = template_files[i]  # exact filename to use
            self.mapping.append({
                "src_path": os.path.join(tdir, old),
                "dst_name": new
            })
            self.tree.insert("", "end", values=(old, new, "พร้อม"))
        
        if len(target_files) != len(template_files):
            messagebox.showerror("จำนวนไฟล์ไม่ตรงกัน", "ไฟล์ในสองโฟลเดอร์ต้องมีจำนวนเท่ากัน และเรียงตามตัวอักษรเหมือนกัน\n(ตอนนี้แสดงพรีวิวเฉพาะคู่ที่จับได้)")
    
    def do_rename(self):
        if not self.mapping:
            messagebox.showwarning("ยังไม่มีรายการ", "กรุณากด 'สแกน & พรีวิว' ก่อน")
            return
        
        # Final safety: ensure counts match exactly
        tdir = self.target_dir.get().strip()
        sdir = self.template_dir.get().strip()
        target_files = [f for f in os.listdir(tdir) if os.path.isfile(os.path.join(tdir,f)) and not f.startswith(".")]
        template_files = [f for f in os.listdir(sdir) if os.path.isfile(os.path.join(sdir,f)) and not f.startswith(".")]
        if len(target_files) != len(template_files):
            messagebox.showerror("ยกเลิก", "จำนวนไฟล์ไม่เท่ากัน — ยกเลิกการเปลี่ยนชื่อ")
            return
        
        if not messagebox.askyesno("ยืนยัน", "ยืนยันการเปลี่ยนชื่อไฟล์ทั้งหมดตามพรีวิว?"):
            return
        
        # Two-phase rename: avoid collisions by renaming to temporary names first
        temp_map = []
        try:
            # Phase 1: temp rename
            for item in self.mapping:
                src = item["src_path"]
                base, ext = os.path.splitext(os.path.basename(src))
                tmp_name = f".renametmp_{uuid.uuid4().hex}{ext}"
                tmp_path = os.path.join(os.path.dirname(src), tmp_name)
                os.rename(src, tmp_path)
                temp_map.append((tmp_path, item["dst_name"]))
            
            # Phase 2: final names (exactly as template filename)
            used = set()
            for tmp_path, final_name in temp_map:
                dst_path = os.path.join(self.target_dir.get().strip(), final_name)
                if final_name in used or os.path.exists(dst_path):
                    # If exists (e.g., template name equals another target's old name), append numeric suffix
                    name, ext = os.path.splitext(final_name)
                    k = 1
                    new_final = f"{name} ({k}){ext}"
                    while new_final in used or os.path.exists(os.path.join(self.target_dir.get().strip(), new_final)):
                        k += 1
                        new_final = f"{name} ({k}){ext}"
                    final_name = new_final
                    dst_path = os.path.join(self.target_dir.get().strip(), final_name)
                os.rename(tmp_path, dst_path)
                used.add(final_name)
            
            messagebox.showinfo("สำเร็จ", "เปลี่ยนชื่อไฟล์เรียบร้อย")
            self.scan_preview()
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", f"{type(e).__name__}: {e}")
            # Attempt rollback: nothing to do safely here because we may not know original names now.
            # User can re-run preview to see current state.
        
if __name__ == "__main__":
    app = RenamerApp()
    app.mainloop()
