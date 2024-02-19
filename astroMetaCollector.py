from astropy.io import fits
import os
import csv

directory = os.getcwd()

filepath = directory + "\\LIGHTS"

csv_data = []
date_exposure_filter_data = {}

filter_replacements = {
    "L": "Antila 2\" Luminance Filter",
    "R": "Antila 2\" Red Filter",
    "G": "Antila 2\" Green Filter",
    "B": "Antila 2\" Blue Filter",
    "Ha": "Astronomik 2\" 6nm Ha Filter",
    "O3": "Astronomik 2\" 6nm O3 Filter",
    "S2": "Astronomik 2\" 6nm S2 Filter"
}

filter_replacements_astrobin = {
    "L": "53",
    "R": "58",
    "G": "63",
    "B": "58",
    "Ha": "403",
    "O3": "413",
    "S2": "423"
}

# Store additional information
earliest_date = None
latest_date = None
lights_data = {}
used_filters = set()

# Separate dictionaries for general use and AstroBin
data_for_general_use = []
data_for_astrobin = []

for root, subdirs, files in os.walk(filepath):
    for file in files:
        if file.endswith('.fits'):
            f = os.path.join(root, file)
            with fits.open(f) as hdul:
                filter = hdul[0].header['filter']
                exposure = hdul[0].header['exposure']
                dateMagic = str(hdul[0].header['date-loc']).split("T", 1)[0]

                date_exposure_filter_tuple = (dateMagic, exposure, filter)
                if date_exposure_filter_tuple not in date_exposure_filter_data:
                    date_exposure_filter_data[date_exposure_filter_tuple] = {
                        "Date": dateMagic,
                        "Exposure": exposure,
                        "Filter": filter,  # Original filter value
                        "Count": 1
                    }
                else:
                    date_exposure_filter_data[date_exposure_filter_tuple]["Count"] += 1

                # Store data for general use with filter replacements
                data_for_general_use.append({
                  "Date": dateMagic,
                  "Exposure": exposure,
                  "Filter": filter_replacements.get(filter, filter),
                  "Count": 1
                })

                # Store original data for AstroBin without replacements
                data_for_astrobin.append({  # Create a new dictionary for AstroBin data
                  "Date": dateMagic,
                  "Exposure": exposure,
                  "Filter": filter,
                  "Count": 1
                })

                # Track earliest and latest dates
                if earliest_date is None or dateMagic < earliest_date:
                    earliest_date = dateMagic
                if latest_date is None or dateMagic > latest_date:
                    latest_date = dateMagic

                # Track lights frames
                lights_key = (exposure, filter)
                if lights_key not in lights_data:
                    lights_data[lights_key] = 1
                else:
                    lights_data[lights_key] += 1

                # Track used filters
                used_filters.add(filter)

# Write to CSV (regular file)
with open("results.csv", 'w', newline='') as csvfile:
    fieldnames = ["Date", "Exposure", "Filter", "Count"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data_for_general_use)  # Use data with general filter replacements

# Write to CSV (AstroBin-compatible format)
with open("AstroBin.csv", 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["date", "duration", "filter", "number"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Extract and format data for AstroBin
    for data in date_exposure_filter_data.values():  # Access data from the correct dictionary
        astrobin_data = {
            "date": data["Date"].split("T")[0],  # Line 64: Access "Date" from the correct dictionary
            "duration": f"{data['Exposure']:.4f}",
            "filter": filter_replacements_astrobin.get(data["Filter"], data["Filter"]),
            "number": data["Count"]
        }
        writer.writerow(astrobin_data)

# Generate text file content
with open("reddit_template.txt", "w") as text_file:
    text_file.write("Astrobin: \n\n")
    text_file.write(f"Captured {earliest_date} - {latest_date}\n\n")
    text_file.write("Bortle 6 Sky (east SF Bay area)\n\n")
    text_file.write("Equipment|||\n:--|:--|:--|\n")
    text_file.write("Celestron EdgeHD 8\" | Celestron .7x Reducer | ZWO ASI2600MM Pro\n")
    text_file.write("SkyWatcher EQ6-Ri Pro | Celestron OAG | ZWO ASI174MM-Mini\n")
    text_file.write("ZWO EAF | ZWO 7x2\" EFW | NINA/PHD2/GS\n\n")

    # Filters table
    text_file.write("Filters|||\n:--|:--|:--|\n")  # Table title

    # Sort alphabetically based on filter replacement text
    sorted_filters = sorted(used_filters, key=lambda f: filter_replacements[f])  # Sort by replacement text

    # Generate table rows with sorted filters
    filters_rows = []
    filters_row = []
    for filter in sorted_filters:  # Iterate over the sorted filters
        filters_row.append(filter_replacements[filter])

        if len(filters_row) == 3:  # Limit to 3 entries per row
            filters_rows.append(filters_row)
            filters_row = []

    if filters_row:  # Add any remaining entries
        filters_rows.append(filters_row)

    for row in filters_rows:
        text_file.write(f"{' | '.join(row)}\n")  # Add spaces around delimiters

    text_file.write("\n")  # Add a blank line

    # Data table
    text_file.write(f"Data|||\n:--|:--|:--|\n")

    # Calculate total number of FITS files
    total_fits_files = sum(count for count in lights_data.values())

    lights_list = []
    for (exposure, filter), count in lights_data.items():
        lights_list.append(f"{count}x{exposure}s {filter}")
    # Lights row with literal "x"
    text_file.write(
        f"Lights|{total_fits_files}|{', '.join(f'{int(count)}x{int(exposure)}s{filter}' for (exposure, filter), count in lights_data.items())}\n"
    )
    text_file.write(f"Flats|{20 * len(used_filters)}| {', '.join(f'20{filter}' for filter in used_filters)}\n")

    # Unique exposure lengths (as integers)
    unique_exposures = {int(exposure) for exposure, _ in lights_data.keys()}  # Convert to integers during extraction

    # Darks row with integer exposure lengths
    text_file.write(
        f"Darks|{20 * len(unique_exposures)}|{', '.join(f'20x{int(exposure)}s' for exposure in unique_exposures)}\n"
    )

    text_file.write("Biases|200|\n\n")

    # Miscellaneous
    text_file.write("**Miscellaneous:**\n\n")
    text_file.write("    * 100 gain\n\n")
    text_file.write("    * Cooled to 14F\n\n")
    text_file.write("    * Bin2\n\n")
    text_file.write("**Editing and Stacking:**\n\n")
    text_file.write("* Pre-Processed, Stacked, and Processed in PixInsight (not in any particular order)\n\n")
    text_file.write("* Final Processing in Photoshop\n\n")

