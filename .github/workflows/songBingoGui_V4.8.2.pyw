#!/usr/bin/python
##################################### Version 4.8.2 #########################
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import os
import re
import random
import pandas as pd 
import numpy as np
from tinytag import TinyTag 
import csv
import shutil
from pathlib import Path
import platform
from tkinter import messagebox
from tkinter import scrolledtext
from difflib import SequenceMatcher
import webbrowser

###########  variables
os_name = platform.system()
playlist_csv = ''   ###  making only game sheets from playlist.csv file
dir_path = ''
home_dir = Path.home()
###########  functions

def find_dups_window():
   
    """
    Creates a new Toplevel window when called.
    """
    # Create the new Toplevel window, linking it to the main window (root)
    new_window = tk.Toplevel(root)
    new_window.title("Check for duplicate songs")
    new_window.geometry("800x300")
    new_window.attributes('-topmost', True)
    # Add widgets to the new window
    frame1 = tk.Frame(new_window)
    frame1.pack()
    # Add a button to close the new window
    close_button = tk.Button(frame1, text="Close Window", command=new_window.destroy,state='disabled')
    close_button.pack()
    tw = scrolledtext.ScrolledText(new_window, wrap=tk.WORD, width=200, height=50)
    tw.pack(padx=10, pady=10) 
    root_dir = filedialog.askdirectory(title="choose folder to check for dups",parent=new_window)
    close_button.config(text="working...")
    new_window.update_idletasks()
    find_dups(tw,root_dir)
    close_button.config(text="Close Window")
    close_button.config(state='normal')
    
def find_dups(tw,root_dir):
        
        songlist = []
        found_files = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                try:
                    tag = TinyTag.get(full_path)
                    #print(tag.title," - ",tag.artist)
                    if ( tag.title is None or tag.artist is None):
                        continue
                    if re.search(r'Track\s\d',tag.title,re.IGNORECASE) or re.match(r'Unknown artist',tag.artist):
                        continue                        #  change in 2.2
                    
                except Exception as e:
                    #print(f"Error extracting metadata from {full_path}: {e}")
                    continue
                # Check if the entry is a file
                if os.path.isfile(full_path):
                    found_files.append(full_path)
        tw.delete("1.0", tk.END)
        tw.insert(tk.INSERT,f"Processed {len(found_files)} files\n\n")
    
        for file in found_files:   
            file = file.rstrip() 
            tag = TinyTag.get(file)
            title = tag.title
            artist_name = tag.artist
            songlist.append([f"{artist_name} - {title}",file])
        
        
        #tw.insert(tk.INSERT,f"Processed {len(songlist)} files\n\n")
        dups = []
        for i in range(len(songlist)):
            item1 = songlist[i][0]
            for j in range(i + 1, len(songlist)):
                item2 = songlist[j][0]
                
                # Perform your comparison here
                matcher = SequenceMatcher(None, item1, item2)
                if matcher.ratio() > .9:
                    dup = f"{songlist[i][0]} - {songlist[i][1]}\n{songlist[j][0]} - {songlist[j][1]}\n"
                    dups.append(dup)   
        
        for found in (dups):
            tw.insert(tk.INSERT,found)
        


def select_mode():
    global playlist_csv
    global dir_path
    global var1
    bw1.configure(state='disabled')
    folderName.set("")
    var1.set("")
    
    if var.get() == 0:
        playlist_csv= filedialog.askopenfilename(title="Choose a .csv file to make sheets only", 
                                                 filetypes=(("csv files", "*.csv"),)) # Filter for .csv files)
        if os_name == "Windows":
            playlist_csv = playlist_csv.replace("/", "\\")
        
        if os.path.isfile(playlist_csv):
            bw1.configure(state='normal')
            var1.set(f"Using: {playlist_csv}")
            artistLimit.set(0)
            ew2.configure(state='disabled')
        
    else:                                       ##  radio button for full game clicked
        dir_path = filedialog.askdirectory(title="choose where music files are located")
        if os_name == "Windows":
            dir_path = dir_path.replace("/", "\\")
        
        if os.path.isdir(dir_path):
            var1.set(f"Using: {dir_path}")
            bw1.configure(state='normal')
            ew2.configure(state='normal')
def start_task():
    """Sets the hourglass cursor and schedules the long task."""
    # 1. Change the cursor to 'watch' (hourglass)
    root.config(cursor="watch")
    bw1.configure(state='disabled')
    folderName.set("")
    # Ensure the cursor change is immediately visible
    root.update()

    # 2. Schedule the long function to run after a short delay (e.g., 100ms)
    # This delay allows the GUI event loop to process the cursor change first.
    root.after(100,createGame)
       
def createGame():
    
    global playlist_csv
    global dir_path
    current_datetime = datetime.now()
    formatted_date= current_datetime.strftime("%Y-%m-%d_%H.%M.%S")
    sheetFolder = f"{home_dir}/SongBingoFiles/sheetFolder_{formatted_date}"
    if os_name == "Windows":
        sheetFolder = sheetFolder.replace("/", "\\")
    os.makedirs(sheetFolder, exist_ok=True)
    if playlist_csv:
        shutil.copy(playlist_csv,sheetFolder)    
    playlist_path = f'{sheetFolder}/Playlist.txt'   # has list of names - artists 
    if os_name == "Windows":
        playlist_path = playlist_path.replace("/", "\\")
    def find_music_files(root_dir):
        if playlist_csv:
            return
        #print("root ",root_dir)
        """
        Recursively searches for files
        starting from a given root directory.

        Args:
            root_dir (str): The starting directory for the search.
        

        Returns:
            list: A list of full paths to the found files.
        """
        found_files = []
        totalFromArtist = {}
        final_files = []

        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                #print(filename)
                if re.search(r'Track\s\d',filename,re.IGNORECASE):# skip files named Track 
                    continue

            
                full_path = os.path.join(dirpath, filename)
                    #print(full_path)
                    # check if header is readable

                try:
                    tag = TinyTag.get(full_path)
                    #print(tag.title," - ",tag.artist)
                    if ( tag.title is None or tag.artist is None):
                        continue
                    if re.search(r'Track\s\d',tag.title,re.IGNORECASE) or re.match(r'Unknown artist',tag.artist):
                        continue                        #  change in 2.2
                    
                except Exception as e:
                    #print(f"Error extracting metadata from {full_path}: {e}")
                    continue
                # Check if the entry is a file
                if os.path.isfile(full_path):
                    found_files.append(full_path)
        root.config(cursor="")
        if artistLimit.get() != 0:       ########  there is a limit on the number of songs per artist
            random.shuffle(found_files) # Shuffles the list in-place
            for song in found_files:
                tag = TinyTag.get(song)   
                if tag.artist not in totalFromArtist:
                    totalFromArtist[tag.artist] = 0     # if artist is found for the first time create a key value =0
                totalFromArtist[tag.artist] += 1        # increment the song count for that artist
                
                if totalFromArtist[tag.artist] <= artistLimit.get():   # create a new list of songs by an artist <= the limit set by the user
                    final_files.append(song)
            return final_files      # return the reduced song list 
        else:
            #print(len(found_files))
            return found_files      # return the entire song list

    def create_wmp_playlist(playlist_name, song_list_filepaths):
        if playlist_csv:
            return
        if not playlist_name.endswith(".m3u"):
            playlist_name += ".m3u"

        m3u_content = "#EXTM3U\n\n"
        for song_path in song_list_filepaths:
            
            if os_name == 'Windows':
                song_path = song_path.replace("/", "\\")
            elif os_name == "Linux" or os_name == 'Darwin':
                song_path = song_path.replace("\\", "/")
            
             
            song_path = song_path.rstrip()
            
            if os.path.exists(song_path):
            
                m3u_content += f"{song_path}\n"
            else:
                print(f"Warning: Song not found, skipping: {song_path}")
            m3u_filename = f"{sheetFolder}/{playlist_name}"
            if os_name == "Windows":
                m3u_filename = m3u_filename.replace("/", "\\")   
        try:
            with open(m3u_filename, "w", encoding="utf-8") as f:
                f.write(m3u_content)
            #print(f"Playlist '{playlist_name}' created successfully.")
        except IOError as e:
            print(f"Error creating playlist file: {e}")

    if not playlist_csv:            #####  create playlist.txt file with artist - title
        
        try:
            mp3list =  random.sample(find_music_files(dir_path),numOfSongs.get())     # get all the songs from the music folder you chose
        except ValueError as e:
            messagebox.showerror("Err1", "Not enough songs available for use.  Change a parameter and try again")
            bw1.configure(state='normal')
            folderName.set("")
            shutil.rmtree(sheetFolder)
            root.config(cursor="")
            return
        playlist = []
            
        for mp3file in mp3list:   
            mp3file = mp3file.rstrip() 
            tag = TinyTag.get(mp3file)
            title = tag.title
            artist_name = tag.artist
            playlist.append(f"{title} - {artist_name}")

        with open(playlist_path, 'w',encoding='utf-8', errors='ignore') as f:
        
            for item in playlist:
                try:
                    f.write(f"{item}\n")
                except UnicodeDecodeError:
                    pass
            
            

    def readTextFile(file_path):              # read a text file of songs normal flow
        if playlist_csv:
            return
        try:
            lines_list = []
            with open(file_path, 'r') as file:
                for line in file:
                    stripped_line = line.strip()  # Remove leading/trailing whitespace, including newlines
                    if stripped_line:  # Check if the line is not empty after stripping
                        lines_list.append(stripped_line)
                return lines_list       
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    ########    make gamesheets only from csv file playlist
            
    def process_csv(filepath):
        """
        Reads a CSV file row by row and processes each row.

        Args:
            filepath (str): The path to the CSV file.
        """
        playlist = []
       
        try:
            with open(filepath, 'r',encoding='utf-8', newline='') as csv_file:
                csv_reader = csv.reader(csv_file)

                # Skip the header row if present
                header = next(csv_reader, None)
                

                for row in csv_reader:
                    playlist.append(f"{row[0]} - {row[1]}")        
        except FileNotFoundError:
            print(f"Error: The file '{filepath}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        try:
            reducedPlaylist = random.sample(playlist,numOfSongs.get())
        except ValueError as e:
            messagebox.showerror("Err2", "Not enough songs available for use.  Change a parameter and try again")
            bw1.configure(state='normal')
            folderName.set("")
            shutil.rmtree(sheetFolder)
            root.config(cursor="")
            return

        with open(playlist_path, 'w',encoding='utf-8', errors='ignore') as f:
        
            for item in reducedPlaylist:
                
                try:
                    f.write(f"{item}\n")
                except UnicodeDecodeError:
                    pass
        return reducedPlaylist


    if not playlist_csv:        
        songList= readTextFile(playlist_path)   #######   using the generated text file of songs - artists normal flow
    else:
        songList = process_csv(playlist_csv)     #######  using a playlist.csv file to just make game sheets

        
    def makeSheet(game1,game2):
        data = f"<br>Songs taken from: {var1.get()}<br>Number of songs: {numOfSongs.get()}<br>Limit number of songs per artist: {artistLimit.get()}\
        <br>Free space: {freeSpace.get()}"

        newArray = np.array(game1).reshape(5, 5)  #make a 5x5 array for pandas
        df = pd.DataFrame(newArray)
        html_table1 = df.to_html(index=False,header=False)

        newArray = np.array(game2).reshape(5, 5)  #make a 5x5 array for pandas
        df = pd.DataFrame(newArray)
        html_table2 = df.to_html(index=False,header=False)

        html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            table {{
                border-collapse: collapse;
                margin-bottom: 2px; /* Add space between tables */
            }}
            .table-container {{
                display: flex; /* Enables Flexbox */
                justify-content: center; /* Centers the tables horizontally */
                gap: 10px; /* Adds space between the tables */
                margin: 1px; /* Adds margin around the container */
            }}

            td {{
                border: 1px solid black;
                word-wrap: break-word;
                text-align: center; 
                padding: 2px;
                height: 80px;
                width: 80px;
                font-family: Arial;
                font-size: 10px;
            }}
            </style>
            </head>
            <body>
            
            <div class="table-container">
                {html_table1}
                {html_table2}
            </div>
            <br/> <br/> <br/> <br/>
            <h5>{data}</h5>
            </body>
            </html>
            """
        return html


    #make a number of sheets and save them in a folder 
    # each sheet is two games

    for i in range(numOfSheets.get()):
        try:
            if re.match(r'[Yy]',freeSpace.get()):
               
                    game1 = random.sample(songList,24)  #  pick 24 unique songs for one bingo sheet
                    game1.insert(12,'BINGO')
                    game2 = random.sample(songList,24)
                    game2.insert(12,'BINGO')               
            else:
                game1 = random.sample(songList,25)  #  pick 25 unique songs for one bingo sheet
                game2 = random.sample(songList,25)
        except ValueError as e:
                    messagebox.showerror("Err3", "Not enough songs available for use.  Change a parameter and try again")
                    bw1.configure(state='normal')
                    folderName.set("")
                    shutil.rmtree(sheetFolder)
                    root.config(cursor="")
                    return

        html = makeSheet(game1,game2)
        songFile = f"{sheetFolder}/songBingo_{i}.html"
        try:
            with open(songFile, 'w',encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            print(e)
    if not playlist_csv:
        create_wmp_playlist("musicBingoPlaylist", mp3list)      #  create playlist

    #root.destroy()
    if sheetFolder:  # If a folder was selected
        folderName.set(sheetFolder)
        lb8.config(state='normal')
    
# Change cursor back to default (arrow)
    root.config(cursor="")
    bw1.configure(state='normal')
    root.update()


def readHelpFile():
    helpFile = os.path.join(os.path.abspath("."),"songBingoHelp.docx")
    os.startfile(helpFile)



root = tk.Tk()
root.geometry('650x350')
root.title('SongBingo Game Creator Ver. 4.8.2')
font_bold = ("Arial",10,'bold')

##############    menu  ################
menubar = tk.Menu(root)
root.config(menu=menubar) # Attach the menubar to the root window
file_menu = tk.Menu(menubar, tearoff=0) # tearoff=0 prevents the menu from being detached
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open playlist transfer App", command=lambda: webbrowser.open_new_tab("http://tunemymusic.com"))
file_menu.add_command(label="Open Game Files Folder", command=lambda: os.startfile(f"{Path.home()}/SongBingoFiles"))
file_menu.add_command(label="Find Duplicate Songs", command=find_dups_window)
file_menu.add_command(label="Exit", command=root.destroy) # root.destroy closes the window
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help",command=readHelpFile)
menubar.add_cascade(label="Help", menu=helpmenu)
#################################################
var = tk.IntVar()   # for mode radio buttons
var.set(-1)  # No radio button selected initially
frame1 = tk.LabelFrame(text="Choose what you want to do.",labelanchor='n')
frame1.pack(padx=20,fill='x',pady=10)

radio1 = tk.Radiobutton(frame1, text="sheets only from a .csv playlist",
                        variable=var, value=0,command=select_mode)
radio2 = tk.Radiobutton(frame1, text="full game using your own music",
                        variable=var, value=1,command=select_mode)

radio1.pack(side='left',padx=20)
radio2.pack(side='left',padx=20)



var1 = tk.StringVar()   # show file being used
lb3 = tk.Label(root,textvariable=var1,font=font_bold,relief='flat', wraplength=530).pack(pady=10)

frame2 = tk.Frame()
frame2.pack(padx=10,fill='x')

lb4 = tk.Label(frame2,font=font_bold,text="How many songs to use. min 24(or 25 for no free space games): ")
lb4.pack(side='left')
numOfSongs = tk.IntVar()
numOfSongs.set(40)
ew1 = tk.Entry(frame2,width=3,textvariable=numOfSongs,justify='center')
ew1.pack(side='left',padx=10)

frame3 = tk.Frame()
frame3.pack(padx=10,fill='x')
lb5 = tk.Label(frame3,font=font_bold,text="Limit number of songs per artist. Full game only. 0 means no limit: ")
lb5.pack(side='left')
artistLimit = tk.IntVar()
artistLimit.set(0)
ew2 = tk.Entry(frame3,width=3,textvariable=artistLimit,justify='center')
ew2.pack(side='left',padx=10)

frame4 = tk.Frame()
frame4.pack(padx=10,fill='x')
lb6 = tk.Label(frame4,font=font_bold,text="How many sheets? There are 2 games per sheet: ")
lb6.pack(side='left')
numOfSheets = tk.IntVar()
numOfSheets.set(10)
ew3 = tk.Entry(frame4,width=3,textvariable=numOfSheets,justify='center')
ew3.pack(side='left',padx=10)

frame5 = tk.Frame()
frame5.pack(padx=10,fill='x')
lb7 = tk.Label(frame5,font=font_bold,text="Play game with a free space? y or n: ")
lb7.pack(side='left')
freeSpace = tk.StringVar()
freeSpace.set('n')
ew4 = tk.Entry(frame5,width=3,textvariable=freeSpace,justify='center')
ew4.pack(side='left',padx=10)

bw1 = tk.Button(root,text="Create Game",command= start_task,state='disabled')
bw1.pack(pady=10)

folderName = tk.StringVar(root)
folderName.set("Click here to see new game sheet folder")
lb8 = tk.Button(root,state='disabled',cursor='hand2',textvariable=folderName,command=lambda: os.startfile(folderName.get()))
lb8.pack(pady=20)



tk.mainloop()

