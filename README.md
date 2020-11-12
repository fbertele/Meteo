# Meteo
Webpage with a summary of aeronautical metereological informations using Django.

### Use
<code>$ python3 meteo.py <location> [--sat] </code> to load a page with different tabs from different meteorological informations sources.


The tabs are:
* Precipitations 
* Wind 
* Synoptic charts
* Significant weather charts 
* METARs and TAFs of neighbouring airports 
* Satellite images 

Sources: Windy, Metoffice UK, DWD, Aviationweather and Sat24

#### Notice
MapApi is used to get coordinates from location names and an account is required. If you don't want to make one you can pass the coordinates directly in <code> get_info.py </code>
