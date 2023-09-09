# %%
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import hashlib
import json

# %%
def import_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
    
    if file_path:
        global df
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        
        root.withdraw()
        import_or_create_map()

# %%
def process_column(column):
    if not isinstance(column, str):
        column = str(column)
    column = column.strip()
    column = column.upper()
    return column

# %%
def hashing(id):
    hash_object = hashlib.sha512(id.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex

# %%
json_file_path = None
def import_or_create_map():
    json_window = tk.Toplevel(root)
    json_window.title("JSON File Handling")
    json_window.geometry("400x200")
    
    def import_json():
        global json_file_path
        json_file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if json_file_path:
            with open(json_file_path, 'r') as json_file:
                global map
                map = json.load(json_file)
            json_window.destroy()
            get_prefix()
    
    def create_new_map():
        global map
        map = {}
        global json_file_path
        json_file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if json_file_path:
            with open(json_file_path, 'w') as json_file:
                json.dump(map, json_file)
            json_window.destroy()
            get_prefix()
    
    import_button = tk.Button(json_window, text="Import JSON File", command=import_json)
    import_button.pack()
    
    create_button = tk.Button(json_window, text="Create New Map File", command=create_new_map)
    create_button.pack()

# %%
prefix = None

def get_prefix():
    global prefix  
    prefix_window = tk.Toplevel(root)
    prefix_window.title("Prefix Input")
    prefix_window.geometry("400x200")

    tk.Label(prefix_window, text="Enter Prefix (optional):").pack()
    prefix_entry = tk.Entry(prefix_window)
    prefix_entry.pack()

    def handle_mapping_and_export():
        global prefix  
        prefix = prefix_entry.get()
        prefix_window.destroy()
        select_column()

    proceed_button = tk.Button(prefix_window, text="Proceed", command=handle_mapping_and_export)
    proceed_button.pack()

# %%
selected_column = None  

def select_column():
    def process_col():
        global selected_column
        selected_column = column_var.get()
        df[selected_column] = df[selected_column].apply(process_column)
        unique_id_len = df[selected_column].nunique()
        df['hexcode'] = df[selected_column].apply(hashing)
        unique_hash_len = df['hexcode'].nunique()

        if unique_id_len == unique_hash_len:
            column_select_window.destroy()
            handle_mapping(prefix)

        

    column_select_window = tk.Toplevel(root)
    column_select_window.title("Select a Column")
    column_select_window.geometry("400x200")

    tk.Label(column_select_window, text="Select a column:").pack()
    column_var = tk.StringVar(column_select_window)
    column_var.set(df.columns[0])
    column_dropdown = tk.OptionMenu(column_select_window, column_var, *df.columns)
    column_dropdown.pack()

    processcol_button = tk.Button(column_select_window, text="Proceed", command=process_col)
    processcol_button.pack()

# %%
def handle_mapping(prefix):
    if not map:
        last_id = 0
        print(last_id)
    else:
        last_id = max(map.values())
        print(last_id)
    
    for index, hexcode in enumerate(df['hexcode']):
        if hexcode in map:
            df.at[index, selected_column] = f"{prefix}{map[hexcode]}"
        else:
            last_id += 1
            map[hexcode] = last_id
            df.at[index, selected_column] = f"{prefix}{last_id}"

    
    df.drop(columns=['hexcode'], inplace=True)
    print(df)
    print()
    print(map)

    export_map_as_json()
    

# %%
def export_map_as_json():
    if not map:
        return
    
    if json_file_path:
        with open(json_file_path, 'w') as json_file:
            json.dump(map, json_file)
            save_df()

# %%
def save_df():
    save_df_window = tk.Toplevel(root)
    save_df_window.title("Save DataFrame")
    save_df_window.geometry("400x200")

    def save_dataframe():
        file_path = filedialog.asksaveasfilename(filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")])
        if not file_path.endswith((".xlsx", ".csv")):
            file_path += ".xlsx"
        if file_path:
            if file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            save_df_window.destroy()
            completion_window()

    save_button = tk.Button(save_df_window, text="Save DataFrame", command=save_dataframe)
    save_button.pack()

# %%
def completion_window():
    completion_window = tk.Toplevel(root)
    completion_window.title("Completion")
    completion_window.geometry("400x200")

    tk.Label(completion_window, text="Anonymizing completed successfully.").pack()

    def close_completion_window():
        completion_window.destroy()
        root.destroy()  

    close_button = tk.Button(completion_window, text="Close", command=close_completion_window)
    close_button.pack()

# %%
root = tk.Tk()
root.title("File Import and Column Selection")
root.geometry("400x200")

import_button = tk.Button(root, text="Import File", command=import_file)
import_button.pack()

# %%
root.mainloop()


