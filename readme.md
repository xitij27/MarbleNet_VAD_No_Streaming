### Resources provided in this zip file:
```
For_SpeechLab/
    ├── chunked_audio/
    │   ├── ali_far_train_trimmed/
    │   ├── ami_far_traim_trimmed/
    │   ├── ali_far_train_non_speech_manifest.json
    │   ├── ali_far_train_speech_manifest.json
    │   ├── ami_far_train_non_speech_manifest.json
    │   ├── ami_far_train_speech_manifest.json
    │   └── result.txt
    ├── sampled_config_60mins/
    │   ├── ali_far/
    │   │   ├── audio/
    │   │   └── rttm/
    │   └── ami_far/
    │       ├── audio/
    │       └── rttm/
    ├── src
    ├── marblenet_infer.py
    ├── marblenet_lite.yaml
    ├── MarbleNet-3x2x64.nemo
    ├── readme.md
    └── requirements.txt
```

## Notes:
- the **model_checkpoint** was trained with labels of background (0) and speech (1). background refers to non-speech.
- if label of non-speech (0) and speech (1) is preferred. Follow the following steps:<br>
**locate read_chunked_audio_files.py**
```
    └── src/
        ├── folder_audio_utils/
        └── vad/
            └── data_prep/
                └── audio_processing/
                    └── read_chunked_audio_files.py
```
**proceed to line 117 and make the changes of:**
```
change label="background" to label="non-speech"
```
**then locate marblenet_lite.yaml (refer to tree above) file line 8 and make the changes of:**
```
change labels: ['background', 'speech'] to   labels: ['non-speech', 'speech']
```
**Finally in marblenet_infer.py make the changes of:**
```
uncomment line 137
# model.cfg.labels = config.model.labels
```
**run script as per instructed in Readme after these edits.**
- the **chunked_audio folder** should be empty prior to running of marblenet_infer script
- the **sampled_config_60mins** folder contains 30mins ali and 30mins ami train audio. The purpose is to test for inference speed and not accuracy.
- For inferencing of other audio you can sturcture your audio as per the sampled_config_60mins/ folder structure given. **However**, you must ensure that your rttm and audio file has the same basename. e.g. if wav file is **example_1.wav** then rttm must be **example_1.rttm**
- For custom inference you are also required to change the following lines in the ***marblenet_infer.py** script.
```
sampled_data_path = "new_sample_folder_name/"
```
-Final result will be posted to chunk_folder
```
    ├── chunked_audio/
        .
        .
        .
        └── result.txt
```
## Major Reminder for Windows user. **youtokentome** and **texterror** dependencies of nemo-toolkit requires c++ compiler. You have to download the Mircrosoft C++ build tools.
 - Instruction: [stackoverflow](https://stackoverflow.com/questions/29846087/error-microsoft-visual-c-14-0-is-required-unable-to-find-vcvarsall-bat#:~:text=find%20vcvarsall.bat-,The%20solution%20is%3A,-Go%20to%20Build)
## set up environment with the following:
## If you are using conda:
```
conda env create -f nemo-env-frame.yml
conda activate nemo-frame
```
## Else if you are using bare python without management libraries such as conda, do ensure you have python version >= 3.8.13 and pip >=22.0.4
### create environment:
```
python -m venv nemo-infer
```
## setup environment:
### windows:
```
nemo-infer\Scripts\activate
pip install -r requirements.txt
```
### linux:
```
source nemo-infer/bin/activate
pip install -r requirements.txt
```

## Infer with the following steps:
### - Make sure you are within For_SpeechLab folder. You should be in the same level as chunked_audio folder!
### - then in your terminal execute the command here:
```
python -m marblenet_infer
```