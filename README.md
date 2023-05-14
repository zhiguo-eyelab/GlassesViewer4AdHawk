# About
This matlab utility can parse recording files from the AdHawk MindLink
eye-tracking glasses. The code was based on the Glasses Viewer tool, 
originaly written by Niehorster etc. (2020) to parse, visualize, and analyze
Tobii Pro Glasses 2/3 data files.

Niehorster, D.C., Hessels, R.S., and Benjamins, J.S. (2020).
GlassesViewer: Open-source software for viewing and analyzing data from
the Tobii Pro Glasses 2 eye tracker. Behavior Research Methods. doi: 10.3758/s13428-019-01314-1](https://doi.org/10.3758/s13428-019-01314-1)

Note that the AdHawk MindLink support added to the original code is experimental.
We will keep updating the code unntil it is functional. A sample recording with 
the MindLink glasses is stored in the "mindlink_raw" folder. To use the Glasses
Viewer tool, first conver the raw MindLink data files into a Tobii project with the
mindlink2GlassProject.py script. Running this script will generate a project in 
the "demo_data" folder, which can then be loaded by the Glasses Viewer.

