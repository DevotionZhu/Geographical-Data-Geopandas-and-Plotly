#!/usr/bin/env python
# coding: utf-8

# # Geogrphical Dataset, Geopandas and Plotly
# 
# This notebook presents how shapefiles and datasets with longitude and latitude data can be manipulated and visualized.
# 
# **Components**
# * Geographical Dataset: Dataset for Exploratory Data Analytics
# * Geopandas: used for Data Processing
# * Plotly: used for Visualiztaion
# 
# **Considerations and Assumptions**
# * For testing, region shapefile is used to minimize processing time
# * For testing, masked sample data is used with over 7k data points
# * User has a mapbox token. Mapbox tokens are offered for free. See https://docs.mapbox.com/help/tutorials/get-started-tokens-api/ on how to create mapbox tokens.
# 
# **Definition of Terms**
# * Dataframe / Dataset - Sample Scraped Data
# * GeoDataFrame / GeoData - Dataframe converted to geometrical data. Long, lat converted geometrically
# * Shapefile - Geospatial data (usually referred to bounded map)
# * Polygon / Overlay - How shapefile is bounded
# * GeoJson - geometrical json file
# 
# **Challenges**
# * Given a polygon from shapefiles and dataset with longitude and latitude columns, how do I 'merge' data from shapefiles to the datapoints?
# * Given a shapefile and a dataset, how do I create a choropleth map using plotly?
# 
# **Objectives**
# 
# 1. Transform shapefiles and dataset for analysis
# 
# 2. Spatially join information from region shapefile to each data point 
# 
# 3. Render choropleth map only basing on shapefile
# 
# **Data Sources**
# * http://philgis.org/country-vector-and-raster-datasets : For shapefiles
# * Sample data : Masked, scraped data of real estate properties

# # Dependencies
# 

# In[76]:


import pandas as pd
import json
import geopandas as gpd
import plotly.graph_objects as go


# # OBJ 1: Transform shapefiles and dataset for analysis
# ## Steps:
# 1. Setup
# 2. Dataset: DataFrame -> GeoDataFrame
# 3. Polygons: Shapefile -> GeoDataFrame
# 4. Shapefile GeoJSON: Shapefile GeoDataFrame -> Shapefile GeoJSON

# ### Step 1: Setup
# Import dataset

# In[33]:


dataset_df = pd.read_json('data/sample_set.json')
dataset_df


# ***(Exploratory Data Analysis)***
# 
# From the table given, we can see that it has geographical coordinates: *attributes.location_longitude*, *attributes_location_latitude*

# ### Step 2: Dataset: DataFrame -> GeoDataFrame
# Dataset needs to be converted to GeoDataFrame to convert coordinate columns to geometrically readable coordinates
# 
# **Reference**
# * https://geopandas.org/gallery/create_geopandas_from_pandas.html 
# 
# **Remark**
# * CRS needs to match. CRS is related to map projection standard. Usually EPSG:4326 is standard. Double check shapefile's CRS data

# In[34]:


dataset_gdf = gpd.GeoDataFrame(dataset_df, geometry=gpd.points_from_xy(dataset_df['attributes.location_longitude'], dataset_df['attributes.location_latitude']), crs='EPSG:4326')
dataset_gdf


# In[70]:


dataset_gdf.plot()


# ***(Exploratory Data Analysis)***
# 
# From the table given, added column for geometry

# ### Step 3: Polygons: Shapefile -> GeoDataFrame
# Shapefile needs to be converted to GeoDataFrame for further data processing

# In[37]:


regions_gdf = gpd.read_file('data/ph_regions.shp')
regions_gdf


# In[38]:


regions_gdf.crs


# In[69]:


regions_gdf.plot()


# ***(Exploratory Data Analysis)***
# 
# From the EDA above, CRS is **EPSG:4326** which validates CRS initialized in **Step 1**

# ### Step 4: Shapefile GeoJSON: Shapefile GeoDataFrame -> Shapefile GeoJSON
# 
# Shapefile needs to be converted to json for visualization

# In[78]:


regions_json = json.loads(regions_gdf.to_json())


# *regions_json results*
# ```
# {'type': 'FeatureCollection',
#  'features': [{'id': '0',
#    'type': 'Feature',
#    'properties': {'REGION': 'Autonomous Region of Muslim Mindanao (ARMM)'},
#    'geometry': {'type': 'MultiPolygon',
#     'coordinates': [[[[119.46694183349618, 4.586939811706523],
# ```

# ***(Exploratory Data Analysis)***
# 
# From json above, it can be seen that under features key, following key-pair value exists: *_id*, *properties*, *geometry*
# 
# **Remark**
# This is important note when setting up the choropleth map

# # OBJ 2: Spatially join information from region shapefile to each data point 
# This maps region polygon / shapefile information to datapoints inside respective polygon

# In[44]:


dataset_x_region = gpd.sjoin(dataset_gdf, regions_gdf, op='within')
dataset_x_region


# # OBJ 3: Render choropleth map only basing on shapefile
# ## Steps:
# 1. Aggregate Dataset for Choropleth Map
# 2. Visualization
# 
# **References**
# * https://chart-studio.plotly.com/~empet/15238/tips-to-extract-data-from-a-geojson-di/#/

# ### Step 1: Aggregate Dataset for Choropleth Map
# 
# Geopandas have functionalities of pandas DataFrame. For choropleth mapping, aggregation is needed to generated the heatmap

# In[54]:


aggregated_data = dataset_x_region[['REGION', 'values']].groupby('REGION').mean().reset_index()
aggregated_data


# ### Step 2: Visualization
# 
# From *Obj 1, Step 4, EDA remark*, shown in the geojson data that *'REGION'* data is nested under properties.
# 
# Thus in `featureidkey`, string should be in format "properties.*idkey*"
# 
# There is common mistake to ignore the prefix "properties" because this is not seen when visualizing the shapefile **GeoDataFrame** table
# 
# Always remember that shapefile needs to be converted to geojson for plotly and mapbox to read the polygons. Which is why prefix is needed since `featureidkey` is read from **geojson** and not from **GeoDataFrame**
# 
# **GeoDataFrame** is just preparatory step to convert **shapefile** to **geojson**

# In[75]:


token = open(".mapbox_token").read().strip()
fig = go.Figure(
    go.Choroplethmapbox(
        geojson=regions_json,
        featureidkey='properties.REGION',
        locations=aggregated_data['REGION'],
        z=aggregated_data['values'],
        colorscale="Viridis"
    )
)
fig.update_layout(mapbox_style="light", mapbox=dict(accesstoken=token))
# Refer to Snapshots


# In[68]:


import plotly.express as px
fig = px.choropleth_mapbox(aggregated_data, geojson=regions_json,
                          featureidkey='properties.REGION', locations='REGION', color='values')
fig.update_layout(mapbox_accesstoken=token)
fig.show()
# Refer to Snapshots

