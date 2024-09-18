import tkinter as tk
from tkinter import ttk, messagebox
import re
import webbrowser

# File path for the Bible text file
BIBLE_PATH = "C:\Bible\HolyBible.txt"

class BibleSearchApp:
    
    def __init__(self, master):
        self.master = master
        master.title("Bible Word Search")
        master.geometry("800x700")

        # Create and place widgets
        self.create_widgets()

    def create_widgets(self):
        # Search frame
        search_frame = ttk.Frame(self.master, padding="10 10 10 0")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Enter a word:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", self.search_bible)

        ttk.Button(search_frame, text="Search", command=self.search_bible).pack(side=tk.LEFT)
        self.copy_all_button = ttk.Button(search_frame, text="Copy All", command=self.copy_all)
        self.copy_all_button.pack(side=tk.LEFT, padx=5)

        self.results_count = ttk.Label(search_frame, text="")
        self.results_count.pack(side=tk.RIGHT)

        # Results frame
        results_frame = ttk.Frame(self.master, padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview for results
        self.tree = ttk.Treeview(results_frame, columns=("Book", "Chapter", "Verse", "Text"), show="headings")
        self.tree.heading("Book", text="Book")
        self.tree.heading("Chapter", text="Chapter")
        self.tree.heading("Verse", text="Verse")
        self.tree.heading("Text", text="Text")
        self.tree.column("Book", width=100, minwidth=100, stretch=tk.NO)
        self.tree.column("Chapter", width=70, minwidth=70, stretch=tk.NO)
        self.tree.column("Verse", width=70, minwidth=70, stretch=tk.NO)
        self.tree.column("Text", width=500, minwidth=200, stretch=tk.YES)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Display frame
        display_frame = ttk.Frame(self.master, padding="10")
        display_frame.pack(fill=tk.X)

        self.display_text = tk.Text(display_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.display_text.pack(fill=tk.X)

        # Open in Bible.com button
        self.open_bible_button = ttk.Button(display_frame, text="Open in Bible.com", command=self.open_in_bible_com)
        self.open_bible_button.pack(pady=5)

        # Status bar
        self.status_bar = ttk.Label(self.master, text="", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.copy_selected)
        self.master.bind("<Control-c>", self.copy_selected)

    def search_bible(self, event=None):
        search_word = self.search_entry.get()
        if not search_word:
            messagebox.showwarning("Input Required", "Please enter a word to search.")
            return

        self.tree.delete(*self.tree.get_children())
        verses = self.search_bible_file(search_word)

        if verses:
            for verse in verses:
                self.tree.insert("", tk.END, values=(verse["Book"], verse["Chapter"], verse["Verse"], verse["Text"]))
            self.results_count.config(text=f"Results found: {len(verses)}")
        else:
            messagebox.showinfo("Search Results", "No results found or an error occurred.")
            self.results_count.config(text="Results found: 0")

    def search_bible_file(self, search_word):
        try:
            with open(BIBLE_PATH, 'r', encoding='utf-8') as file:
                content = file.read()
            pattern = re.compile(r"^(.+?)\s+(\d+):(\d+)\s+(.+)$", re.MULTILINE)
            matches = pattern.finditer(content)
            return [
                {
                    "Book": match.group(1),
                    "Chapter": match.group(2),
                    "Verse": match.group(3),
                    "Text": match.group(4).strip()
                }
                for match in matches
                if re.search(re.escape(search_word), match.group(4), re.IGNORECASE)
            ]
        except Exception as e:
            print(f"Error occurred while searching the Bible file: {e}")
            return None

    def on_select(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            text = "\n".join(f"{self.tree.item(item)['values'][0]} {self.tree.item(item)['values'][1]}:{self.tree.item(item)['values'][2]} - {self.tree.item(item)['values'][3]}" for item in selected_items)
            self.display_text.config(state=tk.NORMAL)
            self.display_text.delete(1.0, tk.END)
            self.display_text.insert(tk.END, text)
            self.display_text.config(state=tk.DISABLED)

    def copy_selected(self, event=None):
        selected_items = self.tree.selection()
        if selected_items:
            text = "\n".join(f"{self.tree.item(item)['values'][0]} {self.tree.item(item)['values'][1]}:{self.tree.item(item)['values'][2]} - {self.tree.item(item)['values'][3]}" for item in selected_items)
            self.master.clipboard_clear()
            self.master.clipboard_append(text)
            self.status_bar.config(text="Copied to clipboard.")
            self.status_bar.after(3000, self.clear_status_bar)

    def copy_all(self):
        all_items = self.tree.get_children()
        if all_items:
            text = "\n".join(f"{self.tree.item(item)['values'][0]} {self.tree.item(item)['values'][1]}:{self.tree.item(item)['values'][2]} - {self.tree.item(item)['values'][3]}" for item in all_items)
            self.master.clipboard_clear()
            self.master.clipboard_append(text)
            self.status_bar.config(text="All results copied to clipboard.")
            self.status_bar.after(3000, self.clear_status_bar)
        else:
            messagebox.showwarning("Copy Failed", "No results to copy.")

    def open_in_bible_com(self):
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]  # Get the first selected item
            book = self.tree.item(item)['values'][0]
            chapter = self.tree.item(item)['values'][1]
            
            # Get the first 3 letters of the book name
            book_url = book[:3].lower()
            
            # Construct the Bible.com URL
            url = f"https://www.bible.com/bible/116/{book_url}.{chapter}"
            
            # Open the URL in the default web browser
            webbrowser.open(url)
        else:
            messagebox.showwarning("Selection Required", "Please select a verse to open in Bible.com.")

    def clear_status_bar(self):
        self.status_bar.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = BibleSearchApp(root)
    root.mainloop()
