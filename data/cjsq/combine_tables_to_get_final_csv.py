import pandas as pd
import os 

OUTPUT_DIR = "./data/cjsq/cleaned"
# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


if __name__ == "__main__":
    # we are aiming to get a time series data so need to select the columns of interest
    column_years = ['2015.0', '2016.0', '2017.0', '2018.0', '2019.0', '2020.0', '2021.0',
       '2022.0', '2023.0', '2024.0']
    # read in q1_2.csv for number of crimes recorded and number of offenders charged
    q1_2 = pd.read_csv("./data/cjsq/processed/overview-tables-September-2024/q1_2.csv")
    q1_2_key = 'Recorded crime or notifiable offence outcome on an all offence basis'
    # select rows of interest and we pull out all the columns relevant to years:
    police_rows_of_interest = ["Recorded crime [note 19][note 20]", "Charged/summonsed [note 19][note 20]",
                        "Out of court disposals (OOCDs) [note 6]"]
    # now we extract the data for each row with column years
    police_data_dict = {}
    for row in police_rows_of_interest:
        q1_2_row = q1_2[q1_2[q1_2_key] == row]
        police_data_dict[row] = q1_2_row[column_years].iloc[0].tolist()
    # turn data dict into a dataframe
    column_years_for_df = [str(int(float(year))) for year in column_years]
    police_df = pd.DataFrame.from_dict(police_data_dict, orient='index', columns=column_years_for_df)
    # now we parse out court data from q3_1.csv
    q3_1 = pd.read_csv("./data/cjsq/processed/overview-tables-September-2024/q3_1.csv")
    # Merge 'Offence type [note 10]' and 'Overview' columns
    q3_1['Combined_Offence'] = q3_1['Offence type [note 10]'] + ' - ' + q3_1['Overview']
    q3_1_key = 'Combined_Offence'
    rows_of_interest = [
        "All offence types - Number of defendants proceeded against at MC",
        "All offence types - Proceedings discontinued or discharged",
        "All offence types - Charge withdrawn or dismissed",
        "All offence types - Convicted at MC",
        "All offence types - Appeared at CC for trial [note 34]",
        "All offence types - Case discontinued at CC",
        "All offence types - Acquitted at CC",
        "All offence types - Convicted at CC",
        "All offence types - Convictions total"
    ]
    court_data_dict = {}
    for row in rows_of_interest:
        q3_1_row = q3_1[q3_1[q3_1_key] == row]
        court_data_dict[row] = q3_1_row[column_years].iloc[0].tolist()
    court_df = pd.DataFrame.from_dict(court_data_dict, orient='index', columns=column_years_for_df)
    # print(court_df)
    # now we get the court remand data for MC and CC
    # need to get data and combine in q4_1.csv, q4_2.csv, q4_3.csv
    q4_1 = pd.read_csv("./data/cjsq/processed/overview-tables-September-2024/q4_1.csv")
    q4_2 = pd.read_csv("./data/cjsq/processed/overview-tables-September-2024/q4_2.csv")
    q4_3 = pd.read_csv("./data/cjsq/processed/overview-tables-September-2024/q4_3.csv")
    # now we need to get the remand data for MC and CC
    # need to get data and combine in q4_2.csv, q4_3.csv
    # combine columns Offence type [note 10] and Remand status for each of the dataframes
    q4_2['Combined_Offence'] = q4_2['Offence type [note 10]'] + ' - ' + q4_2['Remand status']
    q4_3['Combined_Offence'] = q4_3['Offence type [note 10]'] + ' - ' + q4_3['Remand status']
    q4_key = "Combined_Offence"
    remand_rows_of_interest_mc = [
        "All offence types - All offence types total",
        "All offence types - Not applicable or unknown [note 39]",
        "All offence types - Bailed",
        "All offence types - Remanded in custody"
    ]
    remand_rows_of_interest_cc = [
        "All offence types - All offence types total",
        "All offence types - Unknown remand status",
        "All offence types - Bailed",
        "All offence types - Remanded in custody"
    ]
    remand_columns_of_interest = [
        'Number of defendants 2014',
       'Number of defendants 2015', 'Number of defendants 2016',
       'Number of defendants 2017', 'Number of defendants 2018',
       'Number of defendants 2019', 'Number of defendants 2020',
       'Number of defendants 2021', 'Number of defendants 2022',
       'Number of defendants 2023', 'Number of defendants 2024'
    ]
    remand_columns_of_interest_df = [col.split()[-1] for col in remand_columns_of_interest if col in q4_1.columns]
    remand_data_dict = {}
    q4_2_row_prefix = "MC "
    q4_3_row_prefix = "CC "
    for row in remand_rows_of_interest_mc:
        q4_2_row = q4_2[q4_2[q4_key] == row]
        remand_data_dict[q4_2_row_prefix+row] = q4_2_row[remand_columns_of_interest].iloc[0].tolist()
    for row in remand_rows_of_interest_cc:
        q4_3_row = q4_3[q4_3[q4_key] == row]
        remand_data_dict[q4_3_row_prefix+row] = q4_3_row[remand_columns_of_interest].iloc[0].tolist()
    remand_df = pd.DataFrame.from_dict(remand_data_dict, orient='index', columns=remand_columns_of_interest_df)
    # sentencing data in q5_1a.csv
    q5_1a = pd.read_csv("./data/cjsq/processed/overview-tables-September-2024/q5_1a.csv")
    # Merge 'Offence type [note 10]' and 'Overview' columns
    q5_1a['Offence_sentence_type'] = q5_1a['Offence type [note 10]'] + ' - ' + q5_1a['Type of sentence']
    q5_1a_key = 'Offence_sentence_type'
    sentencing_rows_of_interest = [
        "All offence types - Sentenced total",
        "All offence types - Immediate custody [note 12]",
        "All offence types - Suspended sentence",
        "All offence types - Community sentence [note 13]",
        "All offence types - Fine",
        "All offence types - Absolute discharge",
        "All offence types - Conditional discharge",
        "All offence types - Compensation",
        "All offence types - Otherwise dealt with [note 26]",
        "All offence types - Disposal not known",
        "All offence types - Average custodial sentence length (months) [note 15]"
    ]
    sentence_data_dict = {}
    column_years_sentence = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
    for row in sentencing_rows_of_interest:
        q5_1a_row = q5_1a[q5_1a[q5_1a_key] == row]
        sentence_data_dict[row] = q5_1a_row[column_years_sentence].iloc[0].tolist()
    sentence_df = pd.DataFrame.from_dict(sentence_data_dict, orient='index', columns=column_years_sentence)
    # time to combine all the dataframes together
    final_df = pd.concat([police_df, court_df, remand_df, sentence_df], axis=0)
    print(final_df[column_years_sentence])
    os.makedirs(f"{OUTPUT_DIR}/overview-tables-September-2024", exist_ok=True)
    final_df[column_years_sentence].to_csv(f"{OUTPUT_DIR}/overview-tables-September-2024/final_cjsq_data.csv", index=False)
        
