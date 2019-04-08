# pcc-automation
Automation for various tasks required by Pune City Connect

## auto_markers
Objective: populates a .kml file with markers from a comma-separated values (CSV) document using a Python script.

How to use:
1. Download Python3 on your computer if you do not have it already.
For Macs, the best way is outlined here: https://wsvincent.com/install-python3-mac/. 
Follow all the steps except the virtual environment bonus section (this is not required).
For Windows, follow the instructions here: https://docs.python-guide.org/starting/install3/win/.
Note that you will have to install chocolatey as well (https://chocolatey.org/install).
Simply copy and paste command under the `Install with cmd.exe` header into the cmd shell.
2. Clone this repository by clicking the green "Clone or Download" button.
Download the zip file and unzip it. 
3. Open a command line shell (terminal on Mac, cmd on Windows)
4. Change folders to be inside the same `auto_markers` directory.
If you list the files in your current directory (by running `dir` on Windows, `ls` on Mac) you should see `main.py` and `printer.py`.
5. Run the program! 
Upon running it will open a file dialog automatically and ask you to input an existing `.kml` map file.
Select an appropriate map file. 
It will also ask you to input any number of CSV sets of markers from which it will add markers to the map.
To see how the CSV files are formatted, please look at the example provided in this repository under `example.csv`.
To run the program, run `python3 main.py`. 
It will create a new map file named `output.kml`.

There are some options when running the program.

The default behaviour is to attempt to intelligently merge all the new markers into the old map.
The merge strategy is as follows:
- If the person is not included at all in the map, add them as specified
- If the person is included already in the map, delete their old marker and add a new marker
- People are uniquely identified by name so this system will break down if two people have identical names

If you do not wish to perform this intelligent merge, you can specify the `--erase` flag.
This will delete all the markers from the previous map and only add the new markers in the provided .csv file.
To run the program with erase, run `python3 main.py --erase`.
