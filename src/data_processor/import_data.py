import pandas as pd

class ImportSettings:
    def __init__(self):
        self.data = None

    def get_settings(self, path, sheet_name="column_mapping"):
        try:
            df = pd.read_excel(
                path,
                sheet_name
            )
            # Tạo từ điển từ 2 cột System name và Raw name trong file settings
            index_col = df.columns[0]
            df_indexed = df.set_index(index_col)
            final_dict = df_indexed.to_dict(orient='index')
            self.data = final_dict
            return final_dict

        except Exception as e:
            print(f"Lỗi khi đọc tệp: {e}")
            return {}

    def get_rename_dict(self):
        """Trả về: {'Tên Tiếng Việt': 'snake_case'} để rename cột"""
        if not self.data: return {}
        return {v['raw_name']: k for k, v in self.data.items() if 'raw_name' in v}

    def get_dplname_dict(self):
        """Trả về: {'Tên Tiếng Việt': 'snake_case'} để rename cột"""
        if not self.data: return {}
        return {v['display_name']: k for k, v in self.data.items() if 'display_name' in v}

    def get_dtype_dict(self):
        """Trả về: {'snake_case': 'float64'} để ép kiểu"""
        if not self.data: return {}
        return {k: v['dtype'] for k, v in self.data.items() if 'dtype' in v}

    def get_required_columns(self):
        """Trả về danh sách các cột bắt buộc phải có"""
        if not self.data: return []
        return [k for k, v in self.data.items() if v.get('is_req') == True]


class ReadOrder:
    def __init__(self):
        self.data = None

    def read_files(self, file_paths):
        dfs = []
        for f in file_paths:
            try:
                if f.endswith('.csv'):
                    df = pd.read_csv(f)

                elif f.endswith('.xlsx'):
                    df = pd.read_excel(f)

                df.columns = df.columns.str.strip()
                print(f'Raw df columns: {df.columns}')
                dfs.append(df)

            except Exception as e:
                print(f"Lỗi khi đọc file {f}: {e}")
        if not dfs:
            return None
        return pd.concat(dfs, ignore_index=True)

    def process_data(self, df: pd.DataFrame, settings: ImportSettings):
        rename_map = settings.get_rename_dict()
        df = df.rename(columns=rename_map)

        print(f"Col after rename: {df.columns}")

        req_cols = settings.get_required_columns()
        missing_cols = [col for col in req_cols if col not in df.columns]

        if missing_cols:
            print(f"Lỗi: File thiếu các cột bắt buộc: {missing_cols}")
            return None
        else:
            df = df[req_cols]

        dtype_map = settings.get_dtype_dict()
        for col, dtype in dtype_map.items():
            if col in df.columns:
                if dtype == 'float' or dtype == 'int':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif dtype == 'datetime':
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                else:
                    df[col] = df[col].astype(str)

        return df