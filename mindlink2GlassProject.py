import os
import json
import random
import string
import shutil
import glob
from datetime import datetime
import pandas as pd

# parsing an argument to get the folder that contains the original recordings
_raw_folder = os.path.join(os.getcwd(), 'mindlink_raw')

# if a project folder does not exit yet, create one that minic the Tobii G2
# directory structure
_mindlink_proj = os.path.join(os.getcwd(),  'demo_data', 'ml_projects')
if not os.path.exists(_mindlink_proj):
    os.mkdir(_mindlink_proj)

# set up a demo project folder
proj_folder = os.path.join(_mindlink_proj, 'mldemo')
if not os.path.exists(proj_folder):
    os.mkdir(proj_folder)

#!!!! for debugging purposes, let's delete everything in the mindlink demo project folder first
_filelist = glob.glob(os.path.join(proj_folder, "*"))
for _f in _filelist:
    os.system(f'rm -rf {_f}')

# sub-directory for calibrations
cal_folder = os.path.join(proj_folder, 'calibrations')
if not os.path.exists(cal_folder):
    os.mkdir(cal_folder)
# sub-directory for participant info
subj_folder = os.path.join(proj_folder, 'participants')
if not os.path.exists(subj_folder):
    os.mkdir(subj_folder)
# sub-directory for recordings
rec_folder = os.path.join(proj_folder, 'recordings')
if not os.path.exists(rec_folder):
    os.mkdir(rec_folder)

# get all sessions from the _raw_folder
_sessions = [_d for _d in os.listdir(_raw_folder) if not _d == '.DS_Store']
# give each session a unique identifier
sessions = {}
for _s in _sessions:
    _identifier = ''.join(random.sample(string.ascii_lowercase+string.digits, 7))
    sessions[_identifier] = _s

# dump a project.json
proj_json = {
    "pr_id": "mldemo",
    "pr_info": {
        "CreationDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "EagleId": "",
        "Name": "MindLinkDemo"
    },
    "pr_created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }
with open(os.path.join(proj_folder, 'project.json'), 'w') as _proj:
    json.dump(proj_json, _proj)

# # dump a lookup_G2.tsv
# _header = [
#     'ProjectID', 'ParticipantID', 'RecordingID', 'CalibrationID',
#     'ProjectName', 'ProjectCreateTime', 'ParticipantName', 'ParticipantNotes',
#     'RecordingName', 'RecordingStartTime', 'RecordingDurationSecs', 'RecordingNotes',
#     'CalibrationStatus', 'FirmwareVersion', 'HeadUnitSerial', 'RecordingUnitSerial',
#     'EyeCameraSetting', 'SceneCameraSetting'
#     ]

# with open(os.path.join(proj_folder, 'lookup_G2.tsv'), 'w') as _lookup:
#     _lookup.write('\t'.join(_header) + '\n')

# loop over all
for _id, _fd in sessions.items():
    # step 1: # create folders for all sessions
    _sf = os.path.join(rec_folder, _id)
    if not os.path.exists(_sf):
        os.mkdir(_sf)

    # step 2: read the meta_data.json
    _meta_data_file = open(os.path.join(_raw_folder, _fd, 'meta_data.json'), 'r')
    _meta_data =json.load(_meta_data_file)
    user_profile = _meta_data['user_profile']
    camera_config = _meta_data['camera_config']
    meta_version = _meta_data['meta_version']
    recording_config = _meta_data['recording_config']
    custom_tags = _meta_data['custom_tags']
    _manifest = _meta_data['manifest']
    manifest_version = _manifest['manifest_version']
    recording_length_ms = _manifest['recording_length_ms']
    _manifest_entries = _manifest['entries']

    _s_name = user_profile["name"]
    _s_age = user_profile["age"]
    _s_gender = user_profile["gender"]
    _s_ipd_mm = user_profile["ipd_mm"]
    _s_ethnicity = user_profile["ethnicity"]
    _s_right_eye = user_profile["right_eye"]
    _s_left_eye = user_profile["left_eye"]
    _s_nosepiece = user_profile["nosepiece"]
    _s_cal_blob_id = str(user_profile["cal_blob_id"])

    # raw data file parameters
    _par_GAZE = pd.DataFrame(columns = ["type", "file_name", "start_time_ms","end_time_ms", "index"])
    _par_IMU = pd.DataFrame(columns = ["type", "file_name", "start_time_ms","end_time_ms", "index"])
    _par_PUPIL_POSITION = pd.DataFrame(columns = ["type", "file_name", "start_time_ms","end_time_ms", "index"])
    _par_VIDEO = pd.DataFrame(columns = ["type", "file_name", "start_time_ms","end_time_ms", "index"])
    _par_PUPIL_DIAMETER = pd.DataFrame(columns = ["type", "file_name", "start_time_ms","end_time_ms", "index"])
    _par_AUDIO = pd.DataFrame(columns = ["type", "file_name", "start_time_ms","end_time_ms", "index"])
    _par_IPD = pd.DataFrame(columns = ["type", "file_name", "start_time_ms","end_time_ms", "index"])
    _par_BLINK = pd.DataFrame(columns = ["type", "file_name", "start_time_ms","end_time_ms", "index"])

    for _entry in _manifest_entries:
        _type = _entry['type']
        _fn = _entry['file_name']
        _stime = _entry['attribute']['start_time_ms']
        _etime = _entry['attribute']['end_time_ms']
        _idx = _entry['attribute']['index']
        
        # GAZE
        if _type == 'GAZE':
            _par_GAZE.loc[len(_par_GAZE.index)] = [_type, _fn, _stime, _etime, _idx]
        # IMU
        if _type == 'IMU':
            _par_IMU.loc[len(_par_IMU.index)] = [_type, _fn, _stime, _etime, _idx]
        # PUPIL_POSITION
        if _type == 'PUPIL_POSITION':
            _par_PUPIL_POSITION.loc[len(_par_PUPIL_POSITION.index)] = [_type, _fn, _stime, _etime, _idx]
        # VIDEO
        if _type == 'VIDEO':
            _par_VIDEO.loc[len(_par_VIDEO.index)] = [_type, _fn, _stime, _etime, _idx]
        # PUPIL_DIAMETER
        if _type == 'PUPIL_DIAMETER':
            _par_PUPIL_DIAMETER.loc[len(_par_PUPIL_DIAMETER.index)] = [_type, _fn, _stime, _etime, _idx]
        # AUDIO
        if _type == 'AUDIO':
            _par_AUDIO.loc[len(_par_AUDIO.index)] = [_type, _fn, _stime, _etime, _idx]
        # IPD
        if _type == 'IPD':
            _par_IPD.loc[len(_par_IPD.index)] = [_type, _fn, _stime, _etime, _idx]
        # BLINK
        if _type == 'BLINK':
            _par_BLINK.loc[len(_par_BLINK.index)] = [_type, _fn, _stime, _etime, _idx]

    # print('We have %d segments' % (_idx+1))

    # dump a sysinfo.json file to the session folder
    # !!! double-check, we may not need this file
    sysinfo = {"servicemanager_version": "1.25.3-citronkola",
            "fpga_v_maj": 0,
            "fpga_v_min": 0,
            "fpga_v_rel": 62,
            "fpga_variant": "normal",
            "board_type": "PVT Board",
            "hu_serial": "TG02G-010105956192",
            "ru_serial": "TG02B-080105043691",
            "sys_ec_preset": "Indoor",
            "sys_sc_preset": "GazeBasedExposure"
            }
    with open(os.path.join(_sf, 'sysinfo.json'), 'w') as _sysinfo:
        json.dump(sysinfo, _sysinfo)

    # dump the participant info into the session folder
    # _fd = 'zhiguo_2021-02-11_063405'
    _subj_name, _date, _time = _fd.split('_')
    _time = ':'.join([_time[0:2], _time[2:4], _time[4:6]])
    print(f"{_date}T{_time}")
    
    subj = {
        "pa_id": _id, # "vxgtdb2",
        "pa_info": {
            "EagleId": "",
            "Name": _s_name,
            "Notes": ""
            },
        "pa_project": "mindlink",
        "pa_calibration": _s_cal_blob_id, # "3gqkra3",
        "pa_created": f"{_date}T{_time}"
        }
    with open(os.path.join(_sf, 'participant.json'), 'w') as _subj:
        json.dump(subj, _subj)

    # dump calibration info into the calibrations folder, if were not there already
    _subj_info = os.path.join(subj_folder, subj['pa_id'])
    if not os.path.exists(_subj_info):
        os.mkdir(_subj_info)
    with open(os.path.join(_subj_info, 'participant.json'), 'w') as _subj_info:
        json.dump(subj, _subj_info)

    # dump the recording info into the session folder
    rec_info = {
        "rec_id": _id, # "gzz7stc",
        "rec_info": {
            "EagleId": "",
            "Name": _fd,
            "Notes": ""
        },
        "rec_participant": _id, #  "vxgtdb2",
        "rec_project": "mindlink",
        "rec_state": "done",
        "rec_segments": _idx,
        "rec_length": recording_length_ms/1000.,
        "rec_calibration":  _s_cal_blob_id, # "3gqkra3",
        "rec_created": f"{_date}T{_time}",
        "rec_et_samples": int(recording_length_ms/2.0),
        "rec_et_valid_samples": int(recording_length_ms/2.0), # assume all samples are good
        "ts_right_x": -32.5,
        "ts_right_y": -27.0,
        "ts_right_z": -19.0,
        "ts_left_x": 32.5,
        "ts_left_y": -27.0,
        "ts_left_z": -19.0,
        "ts_green_limit_radius": 10.0,
        "ts_yellow_limit_radius": 12.5,
        "video_start_t":_par_VIDEO['start_time_ms'][0]/1000.0,
        "video_end_t":_par_VIDEO['end_time_ms'][len(_par_VIDEO.index) -1]/1000.0
        }

    with open(os.path.join(_sf, 'recording.json'), 'w') as _rec:
        json.dump(rec_info, _rec)

    # dump recording parameters to lookup_G2.tsv
#  _header = [
#     'ProjectID', 'ParticipantID', 'RecordingID', 'CalibrationID',
#     'ProjectName', 'ProjectCreateTime', 'ParticipantName', 'ParticipantNotes',
#     'RecordingName', 'RecordingStartTime', 'RecordingDurationSecs', 'RecordingNotes',
#     'CalibrationStatus', 'FirmwareVersion', 'HeadUnitSerial', 'RecordingUnitSerial',
#     'EyeCameraSetting', 'SceneCameraSetting'
#     ]
    _proj_1 = [
        'mindlink', _id, _id, _id, 'MindLinkConverter',
        f"{_date}T{_time}", _s_name, _fd, f"{_date}T{_time}",
        str(recording_length_ms/1000.), 'calibrated', '1.25.3-citronkola', 
        'TG02G-010105956192', 'TG02B-080105043691',
        'Indoor', 'GazeBasedExposure'
        ]
    with open(os.path.join(proj_folder, 'lookup_G2.tsv'), 'a') as _lookup:
        _lookup.write('\t'.join(_proj_1) + '\n')

    # create a segments folder
    _seg_folder = os.path.join(_sf, 'segments')
    if not os.path.exists(_seg_folder):
        os.mkdir(_seg_folder)  

    # create folders to store segments data & dump the calibration files there
    for _f in range(_idx+1):
        _tmp_fd = os.path.join(_seg_folder, str(_f+1))
        if not os.path.exists(_tmp_fd):
            os.mkdir(_tmp_fd)

        # dump the calibration info
        cal_info = {
            "ca_id":  _s_cal_blob_id, # "3gqkra3",
            "ca_info": {

            },
            "ca_participant":  _id, # "vxgtdb2",
            "ca_state": "calibrated",
            "ca_data": "",
            "ca_error_code": 0,
            "ca_type": "default",
            "ca_created": f"{_date}T{_time}",
            "ca_project": "mindlink"
        }
        with open(os.path.join(_tmp_fd, 'calibration.json'), 'w') as _cal:
            json.dump(cal_info, _cal)

        # dump calibration info into the calibrations folder, if were not there already
        _subj_cal = os.path.join(cal_folder, cal_info['ca_id'])
        if not os.path.exists(_subj_cal):
            os.mkdir(_subj_cal)
        with open(os.path.join(_subj_cal, 'calibration.json'), 'w') as _subj_cal:
            json.dump(cal_info, _subj_cal)

        # dump the segment info 
        _seg_len_ms = int(_par_GAZE['start_time_ms'][_f] - _par_GAZE['start_time_ms'][_f])
        seg_info = {
            "seg_id": _f+1,
            "seg_length": round(_seg_len_ms/1000.),
            "seg_length_us": _seg_len_ms,
            "seg_calibrating": True,
            "seg_calibrated": True,
            "seg_t_start": f"{_date}T{_par_GAZE['start_time_ms'][_f]}",
            "seg_t_stop": f"{_date}T{_par_GAZE['end_time_ms'][_f]}",
            "seg_created": f"{_date}T{_par_GAZE['start_time_ms'][_f]}",
            "seg_end_reason": "api",
            "seg_eyesstream": False
        }
        with open(os.path.join(_tmp_fd, 'segment.json'), 'w') as _seg:
            json.dump(seg_info, _seg)

        # # dump a md5sums file
        # with open(os.path.join(_tmp_fd, 'md5sums'), 'w') as _md5sums:
        #     pass

        # # dump a mems file
        # with open(os.path.join(_tmp_fd, 'mems.tslv.gz'), 'w') as _mems:
        #     pass

        # # dump a livedata.json.gz file to the folder
        # with open(os.path.join(_tmp_fd, 'livedata.json.gz'), 'w') as _livedata:
        #     pass

        # # dump an eyesstream.mp4 file to the folder
        # with open(os.path.join(_tmp_fd, 'eyesstream.mp4'), 'w') as _eyesstream:
        #     pass

        # file naming convention, no suffix (e.g., '-1') is used to name the files
        # when there is only one segment (when the MP4 size is < 1 GB)
        if _idx >1:
            _suffix = '-{_f}'
        else:
            _suffix = ''

        # grab the MindLink scene video and rename it to fullstream.mp4
        _origin = os.path.join(_raw_folder, _fd, f'session{_suffix}.mp4')
        _dest = os.path.join(_tmp_fd, 'fullstream.mp4')
        shutil.copyfile(_origin, _dest)

        # grab the MindLink gaze data and rename it to gaze_data.csv
        _origin = os.path.join(_raw_folder, _fd, f'gaze_data{_suffix}.csv')
        _dest = os.path.join(_tmp_fd, 'gaze_data.csv')
        shutil.copyfile(_origin, _dest)

        # grab the MindLink imu data and rename it to imu_data.csv
        _origin = os.path.join(_raw_folder, _fd, f'imu_data{_suffix}.csv')
        _dest = os.path.join(_tmp_fd, 'imu_data.csv')
        shutil.copyfile(_origin, _dest)
        
        # grab the MindLink pupil diameter data and rename it to pupil_diameter_data.csv
        _origin = os.path.join(_raw_folder, _fd, f'pupil_diameter_data{_suffix}.csv')
        _dest = os.path.join(_tmp_fd, 'pupil_diameter_data.csv')
        shutil.copyfile(_origin, _dest)

        # grab the MindLink pupil position data and rename it to pupil_position_data.csv
        _origin = os.path.join(_raw_folder, _fd, f'pupil_position_data{_suffix}.csv')
        _dest = os.path.join(_tmp_fd, 'pupil_position_data.csv')
        shutil.copyfile(_origin, _dest)