### Github

![](https://img.shields.io/github/license/Ashengaurd/FastDataFile)
![](https://img.shields.io/github/v/release/Ashengaurd/FastDataFile)
![](https://img.shields.io/github/downloads/Ashengaurd/FastDataFile/total)
***

### PYPI

![Downloads](https://static.pepy.tech/personalized-badge/FastDataFile?period=total&units=international_system&left_color=black&right_color=red&left_text=downloads)
![Downloads](https://static.pepy.tech/personalized-badge/FastDataFile?period=month&units=international_system&left_color=black&right_color=red&left_text=this+month)
![Downloads](https://static.pepy.tech/personalized-badge/FastDataFile?period=week&units=international_system&left_color=black&right_color=red&left_text=this+week)
***

### Discord

[![Discord](https://img.shields.io/discord/690930221930643467?label=discord)](https://discord.gg/6exsySK)
***

# FastDataFile

This library is a simple library helping you to establish file datafiles with ease

## How to install

To install just use following command

```shell
pip install fastdatafile
```

If you are looking for latest beta/alpha, you can use following command

```shell
pip install --upgrade git+https://github.com/Ashengaurd/FastDataFile.git
```

***
By installing this library following libraries and their dependencies will be installed too.
> Json & Yaml - Used as basic encoders

# Example
This example JSON file
```json
{
  "Test": {
    "BranchA": 5,
    "BranchB": "Great ;)"
  },
  "TestValue": 1234
}
```

Basic example on how fast datafiles work, `JSONDataFile` is an example here and `YAMLDataFile` is also the same

```py
from FastDataFile import JSONDataFile

"""
    If you set `create_if_missing` to `True` it will create the file if it's missing and will save the `default_data` in it.
    Providing `None` to `default_data` will result of saving an empty data (`{}`)
    
    Arguments shown here are default values, You can ignore them if you want to use the default values.
"""
json_db = JSONDataFile('path/to/file.json', create_if_missing=True, default_data=None, encoding='utf8')

"""
    Data can be nested tree, You can move in the tree by using `.` as seperator.
    
    You can provide the method a type or lambda as cast, It will use it to process data one more time! It's not required! 
"""
print(json_db.get_data('Test.BranchA', cast=int) * 2)
# Prints: 10
print(json_db.get_data('Test.BranchA', cast=str) * 2)
# Prints: 55

"""
    Same rules is applied here for the pathing in the data.  
    
    If `default` is set to `True` it will only apply data if the path do not exists!
"""
json_db.set_data('Test.BranchB', "Hey!")  # Change the data to `Hey!`
json_db.set_data('Test.BranchB', "Hi!", default=True)  # Skips as it exists
json_db.set_data('Test.BranchC', "Hi!", default=True)  # Adds the new path and save the data

"""
    Removes the path and value for ever! (A long time!!!)
"""
json_db.remove('TestValue')

"""
    Removes the data file for ever! (A long time!!!)
    
    You must provide the `confirm` wih `True` or it will not remove the file!
"""
json_db.delete(confirm=True)
```

You can use `YAMLDataFile` instead of `JSONDataFile` and it will be the same, Just another format of file encoding will be used.
***

### ❗ There will be more tutorials and examples at [FastDataFile Wiki](https://git.agmdev.xyz/FastDataFile/wiki) ❗
