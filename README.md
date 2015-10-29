# PIExporter
A python application that drag data to server and secue them automatically

What this little application is going to do:

1\ Read in a data package (let's say, d).

2\ One by one, read out the data form names(scale names) in d, and then:

A\ Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one

B\ Open [form_name]_[date].csv, append the data we have into it, one by one. 


C\ Keep the raw data, and then send back delete commend one by one?

C\ Close file, Log down the action and output to log.txt. If there is an error, email me.
 
