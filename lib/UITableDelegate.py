# Python imports
import os
import numpy as np
import datetime as datetime
import time
import json
from pytz import timezone

# Pythonista imports
import ui


class TData (ui.ListDataSource):
    def __init__(self, scale, items=None):
        ui.ListDataSource.__init__(self, items)
        self.xscale = scale
        
    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell()
        cell.text_label.text = str(self.items[row])
        if self.xscale < 2:
        	cell.text_label.font = ("Helvetica", 10)
        cell.text_label.alignment = ui.ALIGN_CENTER
        return cell
    

class ResultsTable(object):
    def __init__(self, subview_, table_, ac_res, etime_res, xscale, yscale, cwd):
        self.subview = subview_
        self.table = table_
        self.etime = etime_res
        self.ac = ac_res       
        self.xscale = xscale
        self.yscale = yscale
        self.cwd = cwd
        self.log_src = (self.cwd + '/log/log_003.json')
        
        with open(self.log_src) as json_file:
            self.log = json.load(json_file)        
            
        if self.xscale > 2:
            self.spacer = '    '
        else:
            self.spacer = '  '
        self.sorted_etime = sorted(list(self.etime))
        dt_list = []     
        orig_dt_list = []   
        for i in self.etime:
            orig_dt_list.append(i.strftime("%b %d, %Y, %I:%M %p"))
        for i in self.sorted_etime:
            dt_list.append(i.strftime("%b %d, %Y, %I:%M %p"))
        results = []
        for i in dt_list:
            results.append(i + self.spacer + str(round(self.ac[np.where(np.array(orig_dt_list) == i)[0][0]],1)) + ' ppm' + np.array(self.log['Key'])[np.where(np.array(orig_dt_list) == i)[0][0]])

                
        self.table_items = results        
        self.list_source = TData(self.xscale, reversed(self.table_items))
        self.table.data_source = self.list_source
        self.table.delegate.action = self.write_notes
        
    def update_table(self):
        self.table.reload()        
        with open(self.log_src) as json_file:
            self.log = json.load(json_file)    
            
        self.etime = []
        for val in self.log['Etime']:
                tval = datetime.datetime.fromtimestamp(int(val))
                self.etime.append(tval)     
        self.acetone = self.log['Acetone']
        new_sorted_etime = sorted(self.etime)
        dt_list = []
        orig_dt_list = [] 
        for i in new_sorted_etime:
            dt_list.append(i.strftime("%b %d, %Y, %I:%M %p"))
        for i in self.etime:
            orig_dt_list.append(i.strftime("%b %d, %Y, %I:%M %p"))
        results = []
        for i in dt_list:
            results.append(i + self.spacer + str(round(self.acetone[np.where(np.array(orig_dt_list) == i)[0][0]],1)) + ' ppm ' + np.array(self.log['Key'])[np.where(np.array(orig_dt_list) == i)[0][0]])
        self.table.data_source =  TData(self.xscale, reversed(results))
        
    def write_notes(self, sender):
        with open(self.log_src) as json_file:
            self.log = json.load(json_file)

        print(self.list_source.items[sender.selected_row])
        print(sender.selected_row)
        
        self.row_ix = sender.selected_row
        self.log_entry = self.log['Notes'][self.row_ix]
        
        self.tdialog = ui.load_view('tabledialog')
        self.tdialog.name = self.list_source.items[sender.selected_row]
        self.tdialog.frame = (0,0,600,150)
        update_button = self.tdialog['update']
        replace_button = self.tdialog['replace']
        self.tdialog['test_notes'].text = self.log_entry
        update_button.action = self.update_log_notes
        replace_button.action = self.replace_log_notes
        self.tdialog.frame = (0, 0, 600, 150)

        self.tdialog.present('Sheet')
        

    def update_log_notes(self, sender):

        current_entry = self.log_entry
        entry_to_add = self.tdialog['text_entry'].text
        try:
            if entry_to_add[0].isupper():
                try:
                    if current_entry[-1] != '.':
                        spacer = '. '
                    else:
                        spacer = '  '
                except:
                    spacer = ''
            else:
                try:
                    if current_entry[-1] != ',':
                        spacer = ', '
                    else:
                        spacer = '  '
                except:
                    spacer = ''           

            new_entry = self.log_entry + spacer + entry_to_add 
            self.log['Notes'][self.row_ix] = new_entry
            self.log['Key'][self.row_ix]  = "*"
            with open(self.log_src, "w") as outfile:
                json.dump(self.log, outfile)
                    
            self.tdialog['test_notes'].text = self.log['Notes'][self.row_ix]
            self.tdialog['text_entry'].text = ''
    
        except:
            self.tdialog['text_entry'].text = ''
        self.tdialog['text_entry'].end_editing()        
        self.update_table()
        self.table.delegate.action = self.write_notes               
    def replace_log_notes(self, sender):

        current_entry = self.log_entry
        entry_to_add = self.tdialog['text_entry'].text           
        
        self.log['Notes'][self.row_ix] = entry_to_add
        if entry_to_add != '':
            self.log['Key'][self.row_ix]  = "*"  
        else: 
            self.log['Key'][self.row_ix]  = ''          
        with open(self.log_src, "w") as outfile:
            json.dump(self.log, outfile)
                
        self.tdialog['test_notes'].text = self.log['Notes'][self.row_ix]
        self.tdialog['text_entry'].text = ''     
        self.tdialog['text_entry'].end_editing()   
        self.update_table()
        self.table.delegate.action = self.write_notes    
