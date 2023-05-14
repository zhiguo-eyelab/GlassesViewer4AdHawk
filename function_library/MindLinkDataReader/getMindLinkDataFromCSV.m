function x = getMindLinkDataFromCSV(file,qDEBUG)
% read MindLink csv files and store them in a Table

% Gaze,     
% '"Timestamp","Gaze_X","Gaze_Y","Gaze_Z","Gaze_X_Right","Gaze_Y_Right","Gaze_Z_Right",
% "Gaze_X_Left","Gaze_Y_Left","Gaze_Z_Left","Vergence","Image_X","Image_Y","Frame_Index"'

% Pupil diameter
% '"Timestamp","Pupil_Size_Right","Pupil_Size_Left"'

% Pupil position
% '"Timestamp","Pupil_Pos_X_Right","Pupil_Pos_Y_Right","Pupil_Pos_Z_Right",
% "Pupil_Pos_X_Left","Pupil_Pos_Y_Left","Pupil_Pos_Z_Left"'

% IMU,
% '"timestamp","Gyro_X","Gyro_Y","Gyro_Z","Accel_X","Accel_Y","Accel_Z"'

f = fopen(file, 'r');

% get the data and skip the header
x = readtable(file,"TextType","string");

% close the file
fclose(f);

% Print the file path if in debugging mode
if qDEBUG
    fprintf('\nData extracted from %s\n\n', file);
end

% show some data
disp(head(x,3));

end

