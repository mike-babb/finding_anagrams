

def load_matrix_splits(out_file_path:str):


    print('...checking for previously saved matrix splits...')

    # if None: process
    # if not found: process
    # if valid: load
    # file names:
    file_name_list = [
    'n_char_matrix_dict.pkl',
    'single_letter_matrix_dict.pkl',
    'letter_selector_matrix_dict.pkl',
    'nc_ls_matrix_dict.pkl',
    'word_group_df.csv']

    n_found_files = 0
    for fn in file_name_list:
        fpn = os.path.join(out_file_path, fn)
        if os.path.exists(fpn):
            n_found_files += 1
    
    if n_found_files == 5:
        print('...saved matrix splits found, loading...')
        # load the data
        n_char_matrix_dict = load_pickle(in_file_path=out_file_path, 
                                         in_file_name=file_name_list[0])
        
        single_letter_matrix_dict = load_pickle(in_file_path=out_file_path, 
                                         in_file_name=file_name_list[1])
        
        letter_selector_matrix_dict = load_pickle(in_file_path=out_file_path, 
                                         in_file_name=file_name_list[2])
        
        nc_ls_matrix_dict = load_pickle(in_file_path=out_file_path, 
                                         in_file_name=file_name_list[3])
        
        # load the csv
        fpn = os.path.join(out_file_path, file_name_list[4])
        wg_df = pd.read_csv(filepath_or_buffer=fpn)
        
        output = (n_char_matrix_dict,
                  single_letter_matrix_dict,
                  letter_selector_matrix_dict,
                  nc_ls_matrix_dict,
                  wg_df)
    else:
        print('...previously saved matrix splits not found...')        
        output = None

    return output

def save_matrix_splits(out_file_path:str,
                      n_char_matrix_dict:dict,
                  single_letter_matrix_dict:dict,
                  letter_selector_matrix_dict:dict,
                  nc_ls_matrix_dict:dict,
                  wg_df:pd.DataFrame):
    
    file_name_list = [
    'n_char_matrix_dict.pkl',
    'single_letter_matrix_dict.pkl',
    'letter_selector_matrix_dict.pkl',
    'nc_ls_matrix_dict.pkl',
    'word_group_df.csv']

    n_found_files = 0
    print('..checking for previously saved splits...')
    for fn in file_name_list:
        fpn = os.path.join(out_file_path, fn)
        if os.path.exists(fpn):
            n_found_files += 1
    
    if n_found_files != 5:
        print('...split matrices do not exists, saving.')
        save_pickle(file_path = out_file_path,
                    file_name = file_name_list[0],
                    obj=n_char_matrix_dict)
        
        save_pickle(file_path = out_file_path,
                    file_name = file_name_list[1],
                    obj=single_letter_matrix_dict)
        
        save_pickle(file_path = out_file_path,
                    file_name = file_name_list[2],
                    obj=letter_selector_matrix_dict)
        
        save_pickle(file_path = out_file_path,
                    file_name = file_name_list[3],
                    obj=nc_ls_matrix_dict)
        
        fpn = os.path.join(out_file_path, file_name_list[4])
        wg_df.to_csv(path_or_buf=fpn, index = False)        


    return None


def compute_word_counts_by_split(count_dict: dict, db_path: str, db_name: str):
    output_dict = {}
    for cdn, cd in count_dict.items():
        temp_df = (
            pd.DataFrame.from_dict(data=cd, orient="index", columns=["n_words"])
            .reset_index(names="split_value")
            .sort_values(by=["split_value"])
        )
        output_dict[cdn] = temp_df

        # perform some pivot operations to get a sense of the different numbers of words
        if cdn == "word_count_by_n_char_and_letter_selector":
            # extract n_char and the letter_selector_values
            temp_df["key_n_char"] = temp_df["split_value"].map(
                lambda x: "n_" + str(x[0]).zfill(2) + "_chars"
            )
            temp_df["key_letter_selector"] = temp_df["split_value"].map(lambda x: x[1])

            # pivot
            temp_df = (
                pd.pivot_table(
                    data=temp_df,
                    index=["key_letter_selector"],
                    columns=["key_n_char"],
                    values=["n_words"],
                    dropna=False,
                    fill_value=0,
                )
                .astype(int)
                .reset_index(col_level=1)
            )

            # extract the relevant part of the column name
            col_names = [cn[1] for cn in temp_df.columns]

            # set the new column names
            temp_df.columns = col_names

            # get column names with the values of the candidate counts
            col_names = [cn for cn in temp_df.columns if cn[0] == "n"]

            # compute the maximum value
            temp_df["n_max_chars"] = temp_df[col_names].apply(func=max, axis=1)

            # reorder columns
            col_names = temp_df.columns.tolist()
            output_col_names = [col_names[0], col_names[-1]]
            output_col_names.extend(col_names[1:-1])

            temp_df = temp_df[output_col_names]

        # write to the database
        write_data_to_sqlite(
            df=temp_df, table_name=cdn, db_path=db_path, db_name=db_name
        )

    return None



wg_df['n_words'] = 1

blarcho = wg_df.pivot_table(values = 'n_words', columns = 'first_letter', index = 'n_chars', aggfunc = "sum", fill_value =0)

blarcho.to_excel('H:/temp/word_cross_tab.xlsx', index = True)