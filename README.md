# About
This MATLAB utility is designed to parse recording files from the AdHawk 
MindLink eye-tracking glasses. The code is based on the GlassesViewer tool 
originally developed by Niehorster et al. (2020) for parsing, visualizing, 
and analyzing data files from the Tobii Pro Glasses 2/3.

Niehorster, D. C., Hessels, R. S., & Benjamins, J. S. (2020). GlassesViewer: 
Open-source software for viewing and analyzing data from the Tobii Pro 
Glasses 2 eye tracker. Behavior Research Methods. https://doi.org/10.3758/s13428-019-01314-1

Please note that the support for AdHawk MindLink glasses in this code is still
 experimental. We will continue updating the code until it is fully functional. 
 To familiarize yourself with the functionality, we have provided a sample 
 recording with the MindLink glasses, which can be found in the "mindlink_raw" 
 folder. Before using the GlassesViewer tool, you need to convert the raw 
 MindLink data files into a Tobii project using the mindlink2GlassProject.py script. 
 Running this script will generate a project in the "demo_data" folder, which can
  then be loaded into GlassesViewer.

