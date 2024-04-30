import argparse
import datetime
import hashlib
import json
import time
import sqlite3
import sys

def add_entry(entries, text, date=None, tags=None):
    if date is None:
        date = datetime.date.today()
    if tags is None:
        tags = []

    entry_id = hashlib.sha256(text.encode()).hexdigest()  # Generate entry_id based on the text

    # Check if the entry_id already exists in the entries list
    for entry in entries:
        if entry['id'] == entry_id:
            # If it does, generate a new entry_id and check again
            entry_id = hashlib.sha256((text + str(time.time())).encode()).hexdigest()
            break

    entry = {'id': entry_id, 'date': date.strftime('%Y-%m-%d'), 'text': text, 'tags': tags}
    entries.append(entry)

    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS entries (id TEXT PRIMARY KEY, date TEXT, text TEXT, tags TEXT)')
    c.execute('INSERT INTO entries (id, date, text, tags) VALUES (?, ?, ?, ?)', (entry_id, date.strftime('%Y-%m-%d'), text, ', '.join(tags)))
    conn.commit()
    conn.close()

    return entry_id

def get_entries(entries, tags=None, date=None, start_date=None, end_date=None):
    filtered_entries = entries

    if tags is not None:
        filtered_entries = [entry for entry in filtered_entries if set(entry['tags']).intersection(set(tags))]

    if date is not None:
        filtered_entries = [entry for entry in filtered_entries if entry['date'] == date.strftime('%Y-%m-%d')]

    if start_date is not None and end_date is not None:
        filtered_entries = [entry for entry in filtered_entries if start_date.strftime('%Y-%m-%d') <= entry['date'] <= end_date.strftime('%Y-%m-%d')]

    return filtered_entries

def edit_entry(entries, entry_id, text):
    for entry in entries:
        if entry['id'] == entry_id:
            entry['text'] = text

            conn = sqlite3.connect('entries.db')
            c = conn.cursor()
            c.execute('UPDATE entries SET text = ? WHERE id = ?', (text, entry_id))
            conn.commit()
            conn.close()
            break

def load_entries():
    try:
        with open('entries.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []

    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS entries (id TEXT PRIMARY KEY, date TEXT, text TEXT, tags TEXT)')
    conn.commit()
    conn.close()

    return entries

def save_entries(entries):
    with open('entries.json', 'w') as f:
        json.dump(entries, f)
        
def delete_entry(entries, entry_id):
    for i, entry in enumerate(entries):
        if entry['id'] == entry_id:
            del entries[i]

            conn = sqlite3.connect('entries.db')
            c = conn.cursor()
            c.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
            conn.commit()
            conn.close()

            print(f'Entry {entry_id} deleted')
            return

    print(f'No entry found with ID {entry_id}')

def main():
    entries = load_entries()

    parser = argparse.ArgumentParser(description='Journaling app')
    subparsers = parser.add_subparsers(dest='command')

    add_parser = subparsers.add_parser('add', help='Add a new entry')
    add_parser.add_argument('text', help='Text of the entry')
    add_parser.add_argument('-d', '--date', type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(), help='Date of the entry (YYYY-MM-DD)')
    add_parser.add_argument('-t', '--tags', nargs='+', help='Tags of the entry')

    get_parser = subparsers.add_parser('get', help='Get entries')
    get_parser.add_argument('-t', '--tags', nargs='+', help='Tags of the entries')
    get_parser.add_argument('-d', '--date', type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(), help='Date of the entries (YYYY-MM-DD)')
    get_parser.add_argument('--start-date', type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(), help='Start date of the date range (YYYY-MM-DD)')
    get_parser.add_argument('--end-date', type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(), help='End date of the date range (YYYY-MM-DD)')

    edit_parser = subparsers.add_parser('edit', help='Edit an entry')
    edit_parser.add_argument('entry_id', help='ID of the entry to edit')
    edit_parser.add_argument('text', help='New text of the entry')
    
    delete_parser = subparsers.add_parser('delete', help='Delete an entry by ID')
    delete_parser.add_argument('entry_id', help='ID of the entry to delete')

    args = parser.parse_args()

    if args.command == 'add':
        entry_id = add_entry(entries, args.text, args.date, args.tags)
        print(f'Entry added with ID {entry_id}')

    elif args.command == 'get':
        filtered_entries = get_entries(entries, args.tags, args.date, args.start_date, args.end_date)
        for entry in filtered_entries:
            print(f'{entry["id"]} - {entry["date"]} - {entry["text"]} - {" ".join(entry["tags"])}')

    elif args.command == 'edit':
        edit_entry(entries, args.entry_id, args.text)
        print(f'Entry {args.entry_id} edited')
        
    elif args.command == 'delete':
        delete_entry(entries, args.entry_id)

    save_entries(entries)

if __name__ == '__main__':
    main()