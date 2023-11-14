# data-inflation-cpi

A package that contains CPI and inflation data. It also includes Python scripts that are used to produce these data.

## Instructions

1. `python update_cpi_data_bls.py` - updated CPI data files with the latest results from the BLS website
2. `python update_data_files.py` - calculates inflation data and saves it to csv files



## Useful commands

- Root folder with virtual environments

  `cd /Users/yuraic/Documents/Development/python`

- Create new virtual environment

  `python3 -m venv big4credit`

- Activate the virtual environment

  `source big4credit/bin/activate`

- Deactivate the virtual environment 

  `deactivate`

- Install package with pip

  `python -m pip install PACKAGE_NAME`

- Uninstall package with pip

  `python -m pip uninstall PACKAGE_NAME`

- Save packages to recreate the virtual environment later

  `python -m pip freeze > requirements.txt`

- Reinstall all the packages in the new virtual environment 

  `python -m pip install -r requirements.txt`