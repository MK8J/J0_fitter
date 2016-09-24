# J0_fitter

This is a program written in python to determine the recombination current, aka J<sub>0e</sub> at a surface of a solar cell from
quasi steady state photoconductance measurements. The program currently only accepts inputs from a Sinton Instruements excel file, and calculates J<sub>0e</sub> with a variety of published methods.

## Installation

Check you have all the prerequsites installed and then just download the [zipped file](https://github.com/MK8J/J0_fitter/archive/master.zip) and run main.py file located in ./src/J0_fitter/ with python 3.5.

### prerequisites

You need to install [python 3.5](https://www.python.org/ftp/python/3.5.2/python-3.5.2.exe). Make sure you click the "add to path" option during installation for an easy time. Check its install entering
```
python
```
into the command prompt.

Then install the packages:

1. pip: Download [GetPip.py](https://www.google.com.au/url?sa=t&rct=j&q=&esrc=s&source=web&cd=2&cad=rja&uact=8&ved=0ahUKEwir1dnM6abPAhVB1WMKHerlAWIQFgghMAE&url=https%3A%2F%2Fbootstrap.pypa.io%2Fget-pip.py&usg=AFQjCNE8Fo9j_sgo1hBzEoUT39H85hFDrg&sig2=8pRU0vXw69kLHK6ob-BjnA). cd into the downloaded directory and run:

    ```
    python get-pip.py
    ```

  2. Install the following python packages:
      * numpy <sup>1</sup>
      * scipy <sup>1</sup>
      * matplotlib <sup>1</sup>
      * pyqt5

     These can be install with either:

      ```
      pip install package_name
      ```

     <sup>1</sup> For windows distributions please download the package from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/), and then run:

    ```
    pip install downloaded_package_name
    ```
    Make sure to install the numpy+MKL package and not just numpy.

3. Install 2 of my other packages (not available from pip):

  1. Semiconductor: download the wheel form [here](https://github.com/MK8J/semiconductor/tree/master/dist) and run:
    ```
    pip install package name
    ```
  2. PV_analyser [here](https://github.com/MK8J/PV_analysis/tree/master/dist)
    ```
    pip install package name
    ```

## Methods


### J0e/Current recombination prefactor determination
Here are a hosts of methods that are implemented in the program:

1. [Kane and Swanson](http://cat.inist.fr/?aModele=afficheN&cpsidt=8187799)
2. [King, Sinton, and Swanson](http://dx.doi.org/10.1109/16.46368)
3. [Kimmerle *et al* 2014](http://dx.doi.org/10.1016/j.egypro.2014.08.087)
4. [Thomson *et al* 2014](10.1016/j.egypro.2014.08.100)
3. [Kimmerle *et al* 2015](http://dx.doi.org/10.1016/j.solmat.2015.06.043)


For the above methods which are modifications of the Kane and Swanson method the option exist to perform the measurement at:

  1. A single excess carrier density value.
  2. Each excess carrier density value, as suggested by [B. Min *et al*](http://dx.doi.org/10.4229/EUPVSEC20142014-2BO.3.6)

### Determination of lifetime

The program also allows the used to:

1. Use the standard Sinton spread sheet caculations to determine the excess carrier density and lifetime
2. Take the raw measured parameters (PC coil voltage, and reference cell voltage), and caculate lifetime. The coil equipment calibration constants are extracted from the Sinton excel spread sheet.

For external calculations the the models that are taken from the [semiconductor module](https://github.com/MK8J/semiconductor). To emulate Sintons lifetime calculations please use the mobility model "Dannhauser-Krausse_1972".
<!-- 3. [Kimmerle *et al* 2016](http://dx.doi.org/10.1063/1.4939888) -->
