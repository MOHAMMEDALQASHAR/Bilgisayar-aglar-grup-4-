import pandas as pd
import os

def load_network_data(base_path='.'):
    """
    Load network data from CSV files and return structured data.
    
    Args:
        base_path (str): Directory containing the CSV files
        
    Returns:
        tuple: (nodes_df, edges_df, demand_df)
    """
    
    # File paths
    nodes_file = os.path.join(base_path, 'BSM307_317_Guz2025_TermProject_NodeData.csv')
    edges_file = os.path.join(base_path, 'BSM307_317_Guz2025_TermProject_EdgeData.csv')
    demand_file = os.path.join(base_path, 'BSM307_317_Guz2025_TermProject_DemandData.csv')
    
    # Check if files exist
    if not all(os.path.exists(f) for f in [nodes_file, edges_file, demand_file]):
        raise FileNotFoundError("One or more network data CSV files are missing.")
        
    # Load DataFrames (handling semicolon delimiter and comma decimal separator)
    nodes_df = pd.read_csv(nodes_file, sep=';', decimal=',')
    edges_df = pd.read_csv(edges_file, sep=';', decimal=',')
    demand_df = pd.read_csv(demand_file, sep=';', decimal=',')
    
    return nodes_df, edges_df, demand_df
