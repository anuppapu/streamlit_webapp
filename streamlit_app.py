import streamlit as st
import pandas as pd
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import xlrd, os
import base64
import io


def main():
    st.set_page_config(page_title='Data Recon Web Application', layout="wide")
    
    hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            
            footer:after {
                content:'Developed By: Anup Ranjan Das(ICI-Conversion)'; 
                visibility: visible;
                display: block;
                position: relative;
                #background-color: olive;
                color: olive;
                padding: 5px;
                top: 2px;
                         }
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    
    new_title = '<p style="font-family:sans-serif; color:Green; font-size: 42px;">Data Reconciliation Web Application</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    
    #Title
    #st.title('Data Reconciliation Web Application')
    
    #Sidebar Title
    st.sidebar.title("Upload files for Reconciliation")
    
    # Below file types are only allowed to upload
    FILE_TYPES = ["csv", "txt", "xls", "xlsx"]

    # Load first File
    file1 = st.sidebar.file_uploader('Upload 1st File  ', type=FILE_TYPES)

    #Load second File
    file2 = st.sidebar.file_uploader('Upload 2nd File  ', type=FILE_TYPES)

    # Function to merge DF based on All columns
    @st.cache
    def dataframe_difference(df1, df2, jointype, which=None):
        # Compare 2 Dataframes with all the columns
        comparison_df = df1.merge(df2,indicator=True,how=jointype)
    
        if which is None:
            diff_df = comparison_df[comparison_df['_merge'] != 'both']
        else:
            diff_df = comparison_df[comparison_df['_merge'] == which]
        
        #diff_df.to_csv("C:\\Users\\sweta\\Desktop\\diff.csv')
        return diff_df
    
    col1, col2 = st.columns(2)
    totrow1 = 0
    totrow2 = 0
    row1 = 0
    row2 = 0
    row3 = 0
    typef = ''
    type2f = ''
    @st.cache
    def read_file(filename,ftype,delim=None,sheet=None):
        
        if ftype == 'text/plain':
            
            if delim == 'Comma':
                 data = pd.read_csv(filename, sep=',',header=0) 
            elif delim == 'Space':
                 data = pd.read_csv(filename, sep=' ') 
            elif delim == 'Semicolon':
                 data = pd.read_csv(filename, sep=';')  
            elif delim == 'Tab':
                 data = pd.read_csv(filename, sep='\t')   
            elif delim == 'Pipe':
                 data = pd.read_csv(filename, sep='|')   
            
        elif ftype == 'csv' or ftype == 'application/vnd.ms-excel':  
            data = pd.read_csv(filename) 
        else:
            data = pd.read_excel(filename,sheet_name=sheet)
            
        return data  
 
    @st.cache
    def download_excel(df, filename):
        towrite = io.BytesIO()
        downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True) # write to BytesIO buffer
        towrite.seek(0)  # reset pointer
        b64 = base64.b64encode(towrite.read()).decode() 
        fn = filename + '.xlsx'
        linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{fn}">Download excel file</a>'
        return(linko)
    
    @st.cache
    def download_csv(df, filename):
        csv = df.to_csv(index=False).encode()
        b64 = base64.b64encode(csv).decode()
        fn = filename + '.csv'
        href = f'<a href="data:file/csv;base64,{b64}" download="{fn}">Download csv file</a>'
        return href
    
    if file1 is not None: 
        
        with col1:
            
            col1.header("File 1")
            
            if file1.type == 'text/plain':
                delim = st.selectbox("Enter Record Delimeter of File 1",['<Select>','Comma','Space','Semicolon','Tab']) 
                #head = st.radio('Record Header of File 1', ('True', 'False'))
                
                if delim == '<Select>':
                    st.warning("Please select record delimeter Type from Drop Down Box")
                
                if delim != '<Select>':
                    data1 = read_file(file1,file1.type,delim)
                    #data1 = pd.read_csv(file1) 
                    if data1.empty:
                        typef = ''
                        st.write("Data set is empty")
                    else:
                        typef = 'y'
                
            elif file1.type == 'csv' or file1.type == 'application/vnd.ms-excel':  
                data1 = read_file(file1,file1.type)
                if data1.empty:
                    typef = ''
                    st.write("Data set is empty")
                else:
                    typef = 'y'
            
            else:   
                
                cpath = os.path.join(os.getcwd(),file1.name)
                #st.write(cpath)
                
                with open(os.path.join(os.getcwd(),file1.name),"wb") as f:
                    f.write(file1.getbuffer())
                          
                xls = xlrd.open_workbook(cpath)
                sheet = st.selectbox('Select the Sheet Name for File1', xls.sheet_names())
                if sheet:
                    data1 = pd.read_excel(cpath,sheet_name=sheet)
                    #data1 = read_file(cpath,file1.type,sheet=sheet)
                    if data1.empty:
                        typef = ''
                        st.write("Data set is empty")
                    else:
                        typef = 'y'
                    
            if typef == 'y':
                
                totrow1 = len(data1.index)
                gb = GridOptionsBuilder.from_dataframe(data1)  
                gb.configure_pagination()
                gb.configure_side_bar()
                gb.configure_selection(selection_mode="multiple", use_checkbox=True)
                gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",editable=True)
                gridOptions = gb.build()    
                
                AgGrid(data1, gridOptions=gridOptions, enable_enterprise_modules=False,update_mode=GridUpdateMode.SELECTION_CHANGED,
                            fit_columns_on_grid_load=True,)
            
                col1.write("File Name: " + file1.name)
                if file1.type == 'application/vnd.ms-excel':
                    col1.write("File Type: csv")
                if file1.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    col1.write("File Type: xlsx")
                col1.write("File Size: " + str(file1.size/1000) + 'KB')
                st.write("Total Columns: " + str(len(data1.columns)))
                st.write("Total Rows : " + str(len(data1.index)))
                
                
            
#         profile = ProfileReport(data1, title="Recon Data",
#                         correlations={
#                                         "pearson": {"calculate": False},
#                                         "spearman": {"calculate": False},
#                                         "kendall": {"calculate": False},
#                                         "phi_k": {"calculate": False},})            
    if file2 is not None:   
         
        with col2:
            
            col2.header("File 2")
            if file2.type == 'text/plain':
                delim2 = st.selectbox("Enter Record Delimeter of File 2",['<Select>','Comma','Space','Semicolon','Tab', 'Pipe']) 
                #head = st.radio('Record Header of File 1', ('True', 'False'))
                
                if delim2 == '<Select>':
                    st.warning("Please select record delimeter Type from Drop Down Box")
                
                if delim2 != '<Select>':
                    data2 = read_file(file2,file2.type,delim2)
                    #data1 = pd.read_csv(file1) 
                    if data2.empty:
                        type2f = ''
                        st.write("Data set is empty")
                    else:
                        type2f = 'y'
                
            elif file2.type == 'csv' or file2.type == 'application/vnd.ms-excel':  
                
                data2 = read_file(file2,file2.type)
                if data2.empty:
                    type2f = ''
                    st.write("Data set is empty")
                else:
                    type2f = 'y'
                    
            else:  
                cpath2 = os.path.join(os.getcwd(),file2.name)   
                
                with open(os.path.join(os.getcwd(),file2.name),"wb") as f2:
                    f2.write(file1.getbuffer())
                    
                xls2 = xlrd.open_workbook(cpath2)
                sheet2 = st.selectbox('Select the Sheet Name for File 2', xls2.sheet_names())
                if sheet2:
                    #data2 = read_file(file2,file2.type,sheet)
                    data2 = pd.read_excel(cpath2,sheet_name=sheet2)
                    if data2.empty:
                        type2f = ''
                        st.write("Data set is empty")
                    else:
                        type2f = 'y'
            
            if type2f == 'y':
                totrow2 = len(data2.index)
                gb1 = GridOptionsBuilder.from_dataframe(data2)  
                gb1.configure_pagination()
                gb1.configure_side_bar()
                gb1.configure_selection(selection_mode="multiple", use_checkbox=True)
                gb1.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",editable=True)
                grid_Options = gb1.build()
                
                AgGrid(data2,grid_Options=grid_Options, 
                      enable_enterprise_modules=True,
                      update_mode=GridUpdateMode.SELECTION_CHANGED,
                      fit_columns_on_grid_load=True,)
            
                col2.write("File Name: " + file2.name)
                if file2.type == 'application/vnd.ms-excel':
                    col2.write("File Type: csv")
                if file2.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    col2.write("File Type: xlsx")
                col2.write("File Size: " + str(file2.size/1000) + 'KB')
                st.write("Total Columns: " + str(len(data2.columns)))
                st.write("Total Rows : " + str(len(data2.index)))
            
    if (file1 is not None) or (file2 is not None):
        if typef == 'y' or type2f == 'y':
            st.header("Dataset Overview")
        
    if file1 is not None and typef == 'y':
        
        if st.checkbox("Show/Hide First Dataset Overview"):
                # display the text if the checkbox returns True value
                profile1 = ProfileReport(data1, title="Recon Data", correlations=None)
                st_profile_report(profile1)
                
    if file2 is not None and type2f == 'y':  
        
        if st.checkbox("Show/Hide Second Dataset Overview"):
                # display the text if the checkbox returns True value
                profile2 = ProfileReport(data2, title="Recon Data", correlations=None)
                st_profile_report(profile2)
    
    if (file1 is not None) and (file2 is not None):
        st.header("Dataset Reconciliation based on selected columns")
    ind1 = ''
    ind2 = ''
    col3, col4 = st.columns(2)
    if (file1 is not None) and (file2 is not None):
        
        with col3:
            if st.checkbox("Select Key Fields from 1st Dataset"):
                data1_col = st.multiselect('Select Key Fields of 1st File', data1.columns)
                if data1_col:
                    st.write("You have selected: " , data1_col)
                    ind1 = 'Y'
    #if file2 is not None:      
        with col4:
            if st.checkbox("Select Key Fields from 2nd Dataset"):
                data2_col = st.multiselect('Select Key Fields od 2nd File', data2.columns)
                if data2_col:
                    st.write("You have selected: " , data2_col)
                    ind2 = 'Y'
            
        if st.checkbox("Use Key Fields for Reconciliation"): 
            if ind1=='Y' and ind2=='Y':
                
                if st.checkbox("Records only present in First Dataset"):
                    merge_df = pd.merge(data1,data2,left_on=data1_col,right_on=data2_col,indicator=True,how='left')
                    merge_df = merge_df[merge_df['_merge'] != 'both'] 
                    merge_df = merge_df.dropna(axis=1).drop(['_merge'],axis=1)
                    merge_df = merge_df[merge_df.columns[~merge_df.columns.str.endswith('_y')]]
                    merge_df.columns = merge_df.columns.str.replace('_x' , '')
                    #st.write(merge_df)
                    row1 = len(merge_df.index)
                               
                    gb2 = GridOptionsBuilder.from_dataframe(merge_df)  
                    gb2.configure_pagination()
                    gb2.configure_side_bar()
                    gb2.configure_selection(selection_mode="multiple", use_checkbox=True)
                    gb2.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",editable=True)
                    grid2_Options = gb2.build()
                    
                    AgGrid(merge_df,grid2_Options=grid2_Options, enable_enterprise_modules=True,update_mode=GridUpdateMode.SELECTION_CHANGED,
                            fit_columns_on_grid_load=True,)
                    
                    if not merge_df.empty: 
                        col1, col2 = st.columns([0.1,0.3])
                    
                        with col1:
                            st.markdown(download_csv(merge_df, "File1Data_by_keycols_tocsv"), unsafe_allow_html=True)
                        with col2:
                            st.markdown(download_excel(merge_df, "File1Data_by_keycols_toexcel"), unsafe_allow_html=True)
 
                         
                if st.checkbox("Records only present in Second Dataset"):
                    merge_df = pd.merge(data1,data2,left_on=data1_col,right_on=data2_col,indicator=True,how='right')
                    merge_df = merge_df[merge_df['_merge'] != 'both']        
                    merge_df = merge_df.dropna(axis=1).drop(['_merge'],axis=1)
                    merge_df = merge_df[merge_df.columns[~merge_df.columns.str.endswith('_x')]]
                    merge_df.columns = merge_df.columns.str.replace('_y' , '')
                    #st.write(merge_df)
                    row2 = len(merge_df.index)
                    
                    gb3 = GridOptionsBuilder.from_dataframe(merge_df)  
                    gb3.configure_pagination()
                    gb3.configure_side_bar()
                    gb3.configure_selection(selection_mode="multiple", use_checkbox=True)
                    gb3.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",editable=True)
                    grid3_Options = gb3.build()
                    
                    AgGrid(merge_df,grid3_Options=grid3_Options, enable_enterprise_modules=True,update_mode=GridUpdateMode.SELECTION_CHANGED,
                            fit_columns_on_grid_load=True,)
                    
                    if not merge_df.empty: 
                        col1, col2 = st.columns([0.1,0.3])
                    
                        with col1:
                            st.markdown(download_csv(merge_df, "File2Data_by_keycols_tocsv"), unsafe_allow_html=True)
                        with col2:
                            st.markdown(download_excel(merge_df, "File2Data_by_keycols_toexcel"), unsafe_allow_html=True)
 
                    
                if st.checkbox("Records presents in both Datasets"):
                    merge_df = pd.merge(data1,data2,left_on=data1_col,right_on=data2_col,how='inner',suffixes=('_left', '_right'))
                    merge_df = merge_df.dropna(axis=1)
                    #st.write(merge_df)
                    row3 = len(merge_df.index)
                    
                    gb4 = GridOptionsBuilder.from_dataframe(merge_df)  
                    gb4.configure_pagination()
                    gb4.configure_side_bar()
                    gb4.configure_selection(selection_mode="multiple", use_checkbox=True)
                    gb4.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",editable=True)
                    grid4_Options = gb4.build()
                    
                    AgGrid(merge_df,grid4_Options=grid4_Options, enable_enterprise_modules=True,update_mode=GridUpdateMode.SELECTION_CHANGED,
                            fit_columns_on_grid_load=True,)
                    
                    if not merge_df.empty: 
                        col1, col2 = st.columns([0.1,0.3])
                    
                        with col1:
                            st.markdown(download_csv(merge_df, "MatchedData_by_keycols_tocsv"), unsafe_allow_html=True)
                        with col2:
                            st.markdown(download_excel(merge_df, "MatchedData_by_keycols_toexcel"), unsafe_allow_html=True)
 
                    
                if st.checkbox("Records present in any one of Dataset, Not in Both"):
                    merge_df = pd.merge(data1,data2,left_on=data1_col,right_on=data2_col,indicator=True,how='outer',suffixes=('_left', '_right'))
                    merge_df = merge_df[merge_df['_merge'] != 'both']     
                    #st.write(merge_df.drop(['_merge'],axis=1))
                    
                    gb5 = GridOptionsBuilder.from_dataframe(merge_df)  
                    gb5.configure_pagination()
                    gb5.configure_side_bar()
                    gb5.configure_selection(selection_mode="multiple", use_checkbox=True)
                    gb5.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",editable=True)
                    grid5_Options = gb5.build()
                    
                    AgGrid(merge_df,grid5_Options=grid5_Options, enable_enterprise_modules=True,update_mode=GridUpdateMode.SELECTION_CHANGED,
                            fit_columns_on_grid_load=True,)
                    
                    if not merge_df.empty: 
                        col1, col2 = st.columns([0.1,0.3])
                    
                        with col1:
                            st.markdown(download_csv(merge_df, "Data_by_keycols_tocsv"), unsafe_allow_html=True)
                        with col2:
                            st.markdown(download_excel(merge_df, "Data_by_keycols_toexcel"), unsafe_allow_html=True)
 
        
    if (file1 is not None) and (file2 is not None):
        st.header("Dataset Reconciliation based on all columns") 
        if st.checkbox("Use All Fields for Reconciliation"):
                
            if st.checkbox("Records only present in 1st Dataset"):
                
                #st.write(dataframe_difference(data1, data2,'left',which='left_only').dropna(axis=1).drop(['_merge'],axis=1))
                merge_df = dataframe_difference(data1, data2,'left',which='left_only').dropna(axis=1).drop(['_merge'],axis=1)
                gb6 = GridOptionsBuilder.from_dataframe(merge_df)  
                gb6.configure_pagination()
                gb6.configure_side_bar()
                gb6.configure_selection(selection_mode="multiple", use_checkbox=True)
                gb6.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",editable=True)
                grid6_Options = gb6.build()
                    
                AgGrid(merge_df,grid6_Options=grid6_Options, enable_enterprise_modules=True,update_mode=GridUpdateMode.SELECTION_CHANGED,
                            fit_columns_on_grid_load=True,)
                if not merge_df.empty: 
                    col1, col2 = st.columns([0.1,0.3])
                    
                    with col1:
                        st.markdown(download_csv(merge_df, "File1Data_by_Allcols_tocsv"), unsafe_allow_html=True)
                    with col2:
                        st.markdown(download_excel(merge_df, "File1Data_by_Allcols_toexcel"), unsafe_allow_html=True)
 
            if st.checkbox("Records only present in 2nd Dataset"):
                #st.write(dataframe_difference(data1, data2,'right',which='right_only').dropna(axis=1).drop(['_merge'],axis=1))
                merge_df=dataframe_difference(data1, data2,'right',which='right_only').dropna(axis=1).drop(['_merge'],axis=1)
                gb7 = GridOptionsBuilder.from_dataframe(merge_df)  
                gb7.configure_pagination()
                gb7.configure_side_bar()
                gb7.configure_selection(selection_mode="multiple", use_checkbox=True)
                gb7.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",editable=True)
                grid7_Options = gb7.build()
                    
                AgGrid(merge_df,grid7_Options=grid7_Options, enable_enterprise_modules=True,update_mode=GridUpdateMode.SELECTION_CHANGED,
                            fit_columns_on_grid_load=True,)
                if not merge_df.empty: 
                    col1, col2 = st.columns([0.1,0.3])
                    
                    with col1:
                        st.markdown(download_csv(merge_df, "File2Data_by_Allcols_tocsv"), unsafe_allow_html=True)
                    with col2:
                        st.markdown(download_excel(merge_df, "File2Data_by_Allcols_toexcel"), unsafe_allow_html=True)
 
            if st.checkbox("Records present in both the Datasets"):
                #st.write(dataframe_difference(data1, data2,'inner',which='both').dropna(axis=1).drop(['_merge'],axis=1))
                merge_df=dataframe_difference(data1, data2,'inner',which='both').dropna(axis=1).drop(['_merge'],axis=1)
                gb8 = GridOptionsBuilder.from_dataframe(merge_df)  
                gb8.configure_pagination()
                gb8.configure_side_bar()
                gb8.configure_selection(selection_mode="multiple", use_checkbox=True)
                gb8.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",editable=True)
                grid8_Options = gb8.build()
                    
                AgGrid(merge_df,grid8_Options=grid8_Options, enable_enterprise_modules=True,update_mode=GridUpdateMode.SELECTION_CHANGED,
                            fit_columns_on_grid_load=True,)
                
                if not merge_df.empty: 
                    col1, col2 = st.columns([0.1,0.3])
                    
                    with col1:
                        st.markdown(download_csv(merge_df, "MatchedData_by_Allcols_tocsv"), unsafe_allow_html=True)
                    with col2:
                        st.markdown(download_excel(merge_df, "MatchedData_by_Allcols_toexcel"), unsafe_allow_html=True)
 
            if st.checkbox("Records present in any of the Dataset, not in both the Datasets"):
                #st.write(dataframe_difference(data1, data2,'outer'))
                merge_df=dataframe_difference(data1, data2,'outer')
                gb9 = GridOptionsBuilder.from_dataframe(merge_df)  
                gb9.configure_pagination()
                gb9.configure_side_bar()
                gb9.configure_selection(selection_mode="multiple", use_checkbox=True)
                gb9.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum",editable=True)
                grid9_Options = gb9.build()
                    
                AgGrid(merge_df,grid9_Options=grid9_Options, enable_enterprise_modules=True,update_mode=GridUpdateMode.SELECTION_CHANGED,
                            fit_columns_on_grid_load=True,)
            
                if not merge_df.empty: 
                    col1, col2 = st.columns([0.1,0.3])
                    
                    with col1:
                        st.markdown(download_csv(merge_df, "Data_by_Allcols_tocsv"), unsafe_allow_html=True)
                    with col2:
                        st.markdown(download_excel(merge_df, "Data_by_Allcols_toexcel"), unsafe_allow_html=True)
     
if __name__ == "__main__":
    main()
