# src/utils/file_reader.py
def read_source_code():
    # hardcoded every file 
    file_path = "WeLove124/test/project-testcases/01_variables.lol"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return ""
