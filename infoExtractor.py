import re
import os
import pandas as pd


def initialContactExtract(df, right_col, left_col, threshold=10):
    """
    Extracts the initial contact based on force readings. 
    Compares the maximum force readings of the right and left foot 
    to determine which foot stepped down.

    Parameters:
    - df: DataFrame containing the data.
    - right_col, left_col: Column names for right and left force.
    - threshold: Force threshold to consider as a step. Default is 10N.

    Returns:
    - DataFrame containing the initial contact row.
    """

    # Determine which foot stepped down
    drop_col, force_col, drop_label = (left_col, right_col, 'LT') if df[right_col].max(
    ) > df[left_col].max() else (right_col, left_col, 'RT')

    # Drop the unneeded force column
    df = df.drop(drop_col, axis=1)

    # Drop rows where force is below threshold
    df = df[df[force_col] >= threshold]

    # Drop columns based on the stepping foot
    df = df.drop(get_cols_by_label(drop_label, df), axis=1)

    return df.iloc[[0]]


def maxContactExtract(df, right_col, left_col):
    """
    Extracts the row corresponding to the maximum contact force 
    for either the right or the left foot.

    Parameters:
    - df: DataFrame containing the data.
    - right_Fz, left_Fz: Column names indicating right and left force.

    Returns:
    - DataFrame containing the row with the maximum contact force.
    """

    # Determine which foot had the maximum contact force
    drop_col, force_col, drop_label = (left_col, right_col, 'LT') if df[right_col].max(
    ) > df[left_col].max() else (right_col, left_col, 'RT')

    # Drop the unneeded force column
    df = df.drop(drop_col, axis=1)

    # Extract row with maximum force for the stepping foot
    df = df[df[force_col] == df[force_col].max()]

    # Drop columns based on the non-stepping foot
    df = df.drop(get_cols_by_label(drop_label, df), axis=1)

    return df.iloc[[0]]


def get_cols_by_label(label, df):
    """
    Returns a list of column names that contain a given label ('LT' or 'RT'),
    excluding those that contain 'Pelvi' (Pelvis or Pelvic).

    Parameters:
    - label (str): The label to filter columns by ('LT' or 'RT').
    - df (DataFrame): The DataFrame from which column names are extracted.

    Returns:
    - List of column names.
    """

    # Extract column names that contain 'Pelvi'
    drop_pelvis = [col for col in df.columns if re.search('Pelvi', col)]

    # Excluding 'Pelvi' columns, get column names that contain the specified label
    return [col for col in df.columns if re.search(label, col) and col not in drop_pelvis]


def init_df(directory_path):
    """
    Reads all the .csv files in a directory and stores their structure in a dictionary.

    Parameters:
    - directory_path (str): The path where .csv files are located.

    Returns:
    - df_dict (dict): Dictionary with filenames as keys and dataframe structures as values.
    """

    df_dict = {}

    # List all .csv files in the directory
    csv_files = [f for f in os.listdir(directory_path) if os.path.isfile(
        os.path.join(directory_path, f)) and f.endswith('.csv')]

    for fileName in csv_files:
        full_file_path = os.path.join(directory_path, fileName)
        # Get the name of the file without the extension
        file_name_without_ext = os.path.splitext(fileName)[0]
        # Read the file and store only the structure of the dataframe in the dictionary
        df_dict[file_name_without_ext] = pd.read_csv(
            full_file_path, header=3).head(0)

        print(f'DF - {file_name_without_ext} - created successfully')

    return df_dict


def check_folder_file_names(directory_path):
    """
    Compares all the folders in the provided directory to ensure the subfiles have desired patterns.

    Parameters:
    - directory_path (str): The path where the folders are located.

    Returns:
    - A dictionary with folder names as keys and their respective file lists as values.
    - Prints discrepancies between folders, if any.
    """

    # Patterns to match
    patterns = [r'HSUL', r'SLLUL', r'HSL', r'SLLL']

    # A dictionary to store the files in each folder
    folder_files = {}

    # Iterate through the items in the directory
    for item in os.listdir(directory_path):
        folder_path = os.path.join(directory_path, item)

        # Check if the item is a directory
        if os.path.isdir(folder_path):
            # List all files that match the desired patterns
            files_in_folder = [f for f in os.listdir(folder_path) if any(
                re.search(pattern, f) for pattern in patterns)]
            folder_files[item] = files_in_folder

    # Compare the file lists from each folder
    reference_folder = list(folder_files.keys())[0]
    reference_files = set(folder_files[reference_folder])

    for folder, files in folder_files.items():
        if set(files) != reference_files:
            print(
                f"Folder '{folder}' has discrepancies compared to '{reference_folder}'.")

    return folder_files


def changeColmNames(df, test_trial, contact_type):
    """
    Prefixes dataframe columns with the contact type and trial name.

    This function modifies the column names of the input dataframe by 
    prefixing them with the provided contact type and trial name. This 
    can be useful when merging or comparing data across multiple trials 
    or contacts to identify the source of each column.

    Parameters:
    - df (pd.DataFrame): The original dataframe which needs its columns renamed.
    - test_trial (str): The name of the trial file.
    - contact_type (str): The type of contact to be prefixed before the trial name.

    Returns:
    - pd.DataFrame: Dataframe with updated column names.
    """

    # Ensure the input is a pandas DataFrame
    df = pd.DataFrame(df)

    # Iterate over the columns and prefix with contact_type and test_trial
    df.columns = [
        f'{contact_type}_{test_trial} {col[3:] if col.startswith(("LT", "RT")) else col}' for col in df.columns]

    return df


def find_Fz_columns(df):
    """Find the names of the columns for left_Fz and right_Fz."""
    left_pattern = r".*LT.*Fz.*"
    right_pattern = r".*RT.*Fz.*"

    # Use regex search to find column names
    left_Fz = [col for col in df.columns if re.search(left_pattern, col, re.I)]
    right_Fz = [col for col in df.columns if re.search(
        right_pattern, col, re.I)]

    if not left_Fz or not right_Fz:
        # Print columns and ask user for the correct indices
        print("Available columns:")
        for idx, col in enumerate(df.columns):
            print(f"{idx}: {col}")
        left_idx = int(input("Enter the index for left_Fz column: "))
        right_idx = int(input("Enter the index for right_Fz column: "))

        # Return the column names based on user input
        return df.columns[left_idx], df.columns[right_idx]

    return left_Fz[0], right_Fz[0]  # Return the column names found by regex


def rename_trial_files(directory):
    """
    Iterate through each test subject in the directory and rename 
    the trial files by removing the date and time from the filename, 
    except for files named "info.csv".

    Parameters:
    - directory: Root directory containing the test subject folders.
    """
    for subdir, _, files in os.walk(directory):  # Iterates through all subdirectories and files
        for file in files:
            # Check if the file is a CSV and not "info.csv"
            if file.endswith(".csv") and file != "info.csv":
                # Extract trial name by splitting at the last underscore and getting the last part
                trial_name = file.split('_', 1)[-1]
                current_filepath = os.path.join(subdir, file)
                new_filepath = os.path.join(subdir, trial_name)
                os.rename(current_filepath, new_filepath)  # Rename the file
    print("Files renamed successfully!")


def main():
    # Uncomment the below line if you want to manually input the folder path
    # folder = input('Please enter folder name: ')

    # Hardcoded folder path for testing purposes
    folder = '/Users/carlsullivan/Google Drive/College/DrKollock/MILB'
    final_df = pd.DataFrame()

    # rename_trial_files(folder)

    for testSubject in os.listdir(folder):
        testSubjectDir = os.path.join(folder, testSubject)

        # Only process directories
        if os.path.isdir(testSubjectDir):
            subject_results = {'Subjest': testSubject}

            # Loop through files in the test subject directory
            for fileName in os.listdir(testSubjectDir):
                filePath = os.path.join(testSubjectDir, fileName)
                title = os.path.splitext(fileName)[0]

                # Process only .csv files (excluding 'info.csv')
                if fileName.lower().endswith('.csv') and fileName.lower() != 'info.csv':
                    print(f'Processing {testSubject} CSV: {title}')

                    df = pd.read_csv(filePath, low_memory=False, header=2).drop(
                        columns=["time", "Activity", "Marker"])

                    left_Fz, right_Fz = find_Fz_columns(df)

                    initial_contact_df = initialContactExtract(
                        df, right_Fz, left_Fz)
                    max_contact_df = maxContactExtract(df, right_Fz, left_Fz)

                    init_contact_df = changeColmNames(
                        initial_contact_df, title, 'Initial')
                    max_contact_df = changeColmNames(
                        max_contact_df, title, 'Max')

                    # Update the subject results dictionary with combined DataFrame values
                    subject_results.update(init_contact_df.iloc[0].to_dict())
                    subject_results.update(max_contact_df.iloc[0].to_dict())

            # END OF FILE LOOP
            subject_results = {k: [v] for k, v in subject_results.items()}
            final_df = pd.concat(
                [final_df, pd.DataFrame(subject_results)], ignore_index=True)
        # END OF DIRECTORY LOOP
    final_df.to_csv("output.csv", index=False)


# Start processing
main()
