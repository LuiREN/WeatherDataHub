import json
import pandas as pd

def create_annotation_file(file_path, output_path):
    df = pd.read_csv(file_path)
    
    annotation = {
        "file_name": file_path.split("/")[-1],
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "date_range": {
            "start": df['Дата'].min(),
            "end": df['Дата'].max()
        },
        "columns": {
            col: {
                "type": str(df[col].dtype),
                "unique_values": df[col].nunique(),
                "sample_values": df[col].sample(5).tolist()
            } for col in df.columns
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(annotation, f, ensure_ascii=False, indent=4)
