# journal-py
This project contains a python script which helps with journalling. The user can add, get, edit and delete entries, the entries can also be tagged. This was made with the help of AI chatbot.

Features:
Add an entry:
add {text} -t/--tags {tags} -d/--date {date}
  Note: here both tags and date are optional, if not mentioned empty tag will be stored and date is default to current date

Get entry: get all or filtered entries.
get -t/--tags {tags} -d/--date {date} --start-date {date} --end-date {date}
  Note: Here all the options are optional, filter only by tags or by date or by both or specify range, for range both start and end are mandatory.

Edit entry: edit an entry based on identifier. First run the get command and note down the id of the entry you want to edit.
edit {entry_id} {new text}
  Note: Please give the command in this format only.

Delete entry: delete an entry by id.
delete {entry_id}

The entries are stored in local(same location as the script) in 2 files entries.json, entries.db(sqlite format).

This is made for my personal use only, any new features required you can make changes to it.
