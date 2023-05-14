function data = readMindLinkDataFiles(recordingDir,userStreams,qDEBUG)

% read in the MindLink data file and make it conform with the data format
% recognizable by the Viewer

if ~isempty(which('matlab.internal.webservices.fromJSON'))
    jsondecoder = @matlab.internal.webservices.fromJSON;
elseif ~isempty(which('jsondecode'))
    jsondecoder = @jsondecode;
else
    error('Your MATLAB version does not provide a way to decode json (which means its really old), upgrade to something newer');
end

% set file format version. cache files older than this are overwritten with
% a newly generated cache file
fileVersion = 23;

cacheFile = fullfile(recordingDir,'livedata.mat');
qGenCacheFile = ~exist(cacheFile,'file');
if ~qGenCacheFile
    % we have a cache file, check its file version
    cache = load(cacheFile,'fileVersion');
    qGenCacheFile = cache.fileVersion~=fileVersion;
end

if qGenCacheFile || qDEBUG
    % 0 get info about participant and recording
    fid = fopen(fullfile(recordingDir,'recording.json'),'rt');
    recording = jsondecoder(fread(fid,inf,'*char').');
    fclose(fid);
    
    fid = fopen(fullfile(recordingDir,'participant.json'),'rt');
    participant = jsondecoder(fread(fid,inf,'*char').');
    fclose(fid);
    
    expectedFs = round(recording.rec_et_samples/recording.rec_length/50)*50;    % find nearest 50Hz
    
    % video start and end time in seconds
    vid_start_time = recording.video_start_t; 
    vid_end_time = recording.video_start_t; 
    
    if qDEBUG
        fprintf('determined fs: %d Hz\n',expectedFs);
    end
    
    % 1 per segment, read data, concate all csv files of the same type
    %     segments.name
    %     segments.folder
    %     segments.date
    %     segments.bytes
    %     segments.isdir
    %     segments.datenum
    [segments, modes] = FolderFromFolder(fullfile(recordingDir,'segments'), 1)
        
    % read all segments into a table
    gaze = [];
    pupil_diameter = [];
    pupil_center = [];
    imu = [];
    for s=1:length(segments)
        % GAZE
        csv_gaze = fullfile(recordingDir,'segments',segments(s).name,'gaze_data.csv');
        if ~isempty(gaze)
            gaze = [gaze; getMindLinkDataFromCSV(csv_gaze, 1)];
        else
            gaze = getMindLinkDataFromCSV(csv_gaze, 1);
        end
        % PUPIL DIAMETER
        csv_pupil_diameter = fullfile(recordingDir,'segments',segments(s).name,'pupil_diameter_data.csv');
        if ~isempty(pupil_diameter)
            pupil_diameter = [pupil_diameter; getMindLinkDataFromCSV(csv_pupil_diameter, 1)];
        else
            pupil_diameter = getMindLinkDataFromCSV(csv_pupil_diameter, 1);
        end
        % PUPIL CENTER
        csv_pupil_center = fullfile(recordingDir,'segments',segments(s).name,'pupil_position_data.csv');
        if ~isempty(pupil_center)
            pupil_center = [pupil_center; getMindLinkDataFromCSV(csv_pupil_center, 1)];
        else
            pupil_center = getMindLinkDataFromCSV(csv_pupil_center, 1);
        end
        
        % IMU
        csv_imu = fullfile(recordingDir,'segments',segments(s).name,'imu_data.csv');
        if ~isempty(imu)
            imu = [imu; getMindLinkDataFromCSV(csv_imu, 1)];
        else
            imu = getMindLinkDataFromCSV(csv_imu, 1);
        end
    end
    
    % 5 reorganize eye data into binocular data, left eye data and right eye data
    data.device = 'MindLink';
    
    % gaze sample index * Here we trim the recording, just for demo
    % purposes, will need to revisit this data length issue
    nSamp  = min([length(gaze.Timestamp) length(pupil_diameter.Timestamp) length(pupil_center.Timestamp)]);
   
    gaze = gaze(1:nSamp,:);
    pupil_diameter = pupil_diameter(1:nSamp, :);
    pupil_center = pupil_center(1:nSamp, :);
    
    % left eye data
    left = struct();
    left.gidx = (1:length(gaze.Timestamp))';
    left.ts = gaze.Timestamp;
    left.pd = pupil_diameter.Pupil_Size_Left;
    left.pc = table2array(pupil_center(:, 5:7));
    left.gd = table2array(gaze(:, 5:7));
    
    % right eye data
	right = struct();
    right.gidx = (1:length(gaze.Timestamp))';
    right.ts = gaze.Timestamp;
    right.pd = pupil_diameter.Pupil_Size_Right;
    right.pc = table2array(pupil_center(:, 2:4));
    right.gd = table2array(gaze(:, 8:10));
    
    binocular = struct();
    binocular.gidx = (1:length(gaze.Timestamp))';
    binocular.ts = gaze.Timestamp;
    binocular.gp = table2array(gaze(:, 12:13));
    binocular.gp3 = table2array(gaze(:,2:4));
    binocular.nEye = ones(nSamp, 1)*2;
        
    % convert gaze vectors to azimuth elevation
    [la,le] = cart2sph(left.gd(:,1), left.gd(:,2), left.gd(:,3));   % matlab's Z and Y are reversed w.r.t. ours
    [ra,re] = cart2sph(right.gd(:,1), right.gd(:,2), right.gd(:,3));
    left.azi  =  la*180/pi; %-90; % I have checked sign and offset of azi and ele so that things match the gaze position on the scene video in the data file (gp)
    right.azi  =  ra*180/pi; %-90;
    left.ele  = -le*180/pi;
    right.ele  = -re*180/pi;
    
    eye = struct();
    eye.fs = expectedFs;
    eye.left = left;
    eye.right = right;
    eye.binocular = binocular;

    % gyroscope and accelerometer data
    gyroscope = struct();
    gyroscope.ts = imu.Timestamp;
    gyroscope.gy = table2array(imu(:,2:4));
    
    accelerometer = struct();
    accelerometer.ts = imu.Timestamp;
    accelerometer.ac = table2array(imu(:,5:7));
        
    % sync port data *** empty
    syncPort = struct('out', struct('ts', [], 'state',[]), 'in', struct('ts', [], 'state',[]));
    
    % API event, *** empty
    APIevent = struct('ts', [], 'ets', [], 'type',{}, 'tag', {});
    
    % 7 add video sync data to output file
%     assert(issorted( vts.ts,'monotonic'))
%     assert(numel(unique(vts.ts-vts.vts))==length(segments))    % this is an assumption of the fts calculation code below
%     data.video.scene.sync   =  vts;
% 
%     clear vts evts
    
    % 10 determine t0, convert all timestamps to second
    % set t0 as start point of latest video
    t0 = min(eye.left.ts);
    
    eye.left.ts  = eye.left.ts - t0;
    eye.right.ts  = eye.right.ts - t0;
    eye.binocular.ts = eye.binocular.ts - t0;
    gyroscope.ts = gyroscope.ts - t0;
    accelerometer.ts = accelerometer.ts - t0;    
    syncPort.out.ts = syncPort.out.ts - t0;
    syncPort.in.ts = syncPort. in.ts - t0;
    %APIevent.ts = APIevent.ts;
    %video.scene.sync.ts = video.scene.sync.ts - t0;
    
    % 12 check video files for each segment: how many frames, and make frame timestamps
    scene = struct();
    scene.fts = [];
    scene.segframes = [];
    scene.missProp = 0;
    scene.calibration = struct();

    for s=1:length(segments)
        file = 'fullstream.mp4';
        tsoff= 0; %video.scene.sync.ts(video.scene.sync.vts==0);

        fname = fullfile(recordingDir,'segments',segments(s).name, file);
        % get frame timestamps and such from info stored in the mp4
        % file's atoms
        [timeInfo,sttsEntries,atoms,videoTrack] = getMP4VideoInfo(fname);
        % 1. timeInfo (from mdhd atom) contains info about timescale,
        % duration in those units and duration in ms
        % 2. stts table, contains the info needed to determine
        % timestamp for each frame. Use entries in stts to determine
        % frame timestamps. Use formulae described here:
        % https://developer.apple.com/library/content/documentation/QuickTime/QTFF/QTFFChap2/qtff2.html#//apple_ref/doc/uid/TP40000939-CH204-25696
        fIdxs = SmartVec(sttsEntries(:,2),sttsEntries(:,1),'flat');
        timeStamps = cumsum([0 fIdxs]);
        timeStamps = timeStamps/timeInfo.time_scale;
        % last is timestamp for end of last frame, should be equal to
        % length of video
        %floor(timeStamps(end)*1000);
        %timeInfo.duration_ms;
        %assert(floor(timeStamps(end)*1000)==timeInfo.duration_ms,'these should match')
        
        % 3. determine number of frames in file that matlab can read by
        % direct indexing. It seems the Tobii files sometimes have a
        % few frames at the end erroneously marked as keyframes. All
        % those cannot be read by matlab (when using read for a
        % specific time or frame number), so take number of frames as
        % last real keyframe. If not a problem, just take number of
        % frames as last for which we have timeStamp
        lastFrame = [];
        [sf,ef] = bool2bounds(diff(atoms.tracks(videoTrack).stss.table)==1);
        if ~isempty(ef) && ef(end)==length(atoms.tracks(videoTrack).stss.table)
            lastFrame = atoms.tracks(videoTrack).stss.table(sf(end));
        end
        if isempty(lastFrame)
            lastFrame = sum(sttsEntries(:,1));
        end
        
        % now that we know number of readable frames, we may have more
        % timestamps than actually readable frames, throw away ones we
        % don't need as we can't read those frames
        assert(length(timeStamps)>=lastFrame)
        timeStamps(lastFrame+1:end) = [];
        
        % Sync video frames with data by offsetting the timelines for
        % each based on timesync info in tobii data file
        scene.fts = [scene.fts timeStamps+tsoff];
        scene.segframes = [scene.segframes lastFrame];

        % resolution sanity check
%         assert(atoms.tracks(videoTrack).tkhd.width ==atoms.tracks(videoTrack).stsd.width , 'mp4 file weird: video widths in tkhd and stsd atoms do not match')
%         assert(atoms.tracks(videoTrack).tkhd.height==atoms.tracks(videoTrack).stsd.height,'mp4 file weird: video heights in tkhd and stsd atoms do not match')
        scene.width    = atoms.tracks(videoTrack).tkhd.width;
        scene.height   = atoms.tracks(videoTrack).tkhd.height;
        scene.fs       = round(1/median(diff(scene.fts)));    % observed frame rate

        % store name of video files
        scene.file{s}  = fullfile('segments',segments(s).name,file); 
    end
    
    % video struct
    video = struct();
    video.scene = scene;
    
    % mapping the gaze position to the scene 
    eye.binocular.gp(:,1) = eye.binocular.gp(:,1)*scene.width;
    eye.binocular.gp(:,2) = eye.binocular.gp(:,2)*scene.height;
    
    % put all data into a struct
    data = struct();
    data.eye = eye;
    data.video = video;
    data.syncPort = syncPort;
    data.APIevent = APIevent;
    data.gyroscope = gyroscope;
    data.accelerometer = accelerometer;
    
    data.time = struct('startTime', min(eye.left.ts), 'endTime', max(eye.left.ts));
    
    % compute user streams, if any
    if ~isempty(userStreams)
        data = computeUserStreams(data, userStreams);
    end
    
    % store data to cache file
    if isfield(participant.pa_info,'Name')
        data.subjName = participant.pa_info.Name;
    else
        data.subjName = participant.pa_info.name;
    end
    
    if isfield(recording.rec_info,'Name')
        data.recName = recording.rec_info.Name;
    else
        data.recName = recording.rec_info.name;
    end
    
    data.fileVersion        = fileVersion;
    data.userStreamSettings = userStreams;
    save(cacheFile,'-struct','data');
else
    fprintf('loading: %s\n',cacheFile);
    data = load(cacheFile);
    % still output warning messages about holes in video, if any
    checkMissingFrames(data.video, 0.05, 0.1);
    % recompute user streams, if needed because settings changed, or
    % because requested
    qResaveCache = false;
    if ~isequal(userStreams,data.userStreamSettings)
        % settings changed, throw away old and recompute
        if isfield(data,'user')
            data = rmfield(data,'user');
        end
        data = computeUserStreams(data, userStreams);
        qResaveCache = true;
    end
    if ~isempty(userStreams)
        recomputeOnLoad = [userStreams.recomputeOnLoad];
        if any(recomputeOnLoad)
            % one or multiple userStreams are set to recompute on load
            data = computeUserStreams(data, userStreams(recomputeOnLoad));
            qResaveCache = true;
        end
    end
    if qResaveCache
        data.userStreamSettings = userStreams;
        save(cacheFile,'-struct','data');
    end
end
    
end