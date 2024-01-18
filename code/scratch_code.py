

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
