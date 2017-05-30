parent_path=os.path.abspath(os.path.join(scalePath, os.pardir))
grap_path=os.path.abspath(os.path.join(parent_path, os.pardir))
#print grap_path
if not os.path.exists(grap_path + '/processed_data/cleaned_dup_data'):
    os.makedirs(grap_path + '/processed_data/cleaned_dup_data')
cleaned_obj.to_csv(grap_path+ '/processed_data/cleaned_dup_data/' + scaleName+'_cleaned' + '_' + time.strftime("%b_%d_%Y" + '_' + time.strftime("%H_%M_%S") +'.csv'))
print "cleaned "+scaleName+' '+"data saved"

if not os.path.exists(grap_path + '/processed_data/scored_data'):
    os.makedirs(grap_path + '/processed_data/scored_data')
scored_obj.to_csv(grap_path+ '/processed_data/scored_data/' + scaleName+'_scored' + '_' + time.strftime("%b_%d_%Y" + '_' + time.strftime("%H_%M_%S") +'.csv'))
print "scored "+scaleName+' '+"data saved"

if not os.path.exists(grap_path + '/processed_data/wideform_data'):
    os.makedirs(grap_path + '/processed_data/wideform_data')
transed_obj.to_csv(grap_path+ '/processed_data/wideform_data/' + scaleName+'_transed' + '_' + time.strftime("%b_%d_%Y" + '_' + time.strftime("%H_%M_%S") +'.csv'))
print "transed "+scaleName+' '+"data saved"
