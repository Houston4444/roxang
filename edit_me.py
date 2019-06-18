

# edit this python file to make another diatonic bended instrument
# when ready, launch ./diatonic_bender.py

# Choose here the key range of what you edit.
# diatonic_bender will make sfz files for the twelve tones
key_range = "A"

all_bends = {
    # here choose where goes the note when bended (-x semitones, y semitones)
    "A" : (-2, 2),
    "A#": (-1, 2),
    "B" : (-2, 1),
    "C" : (-1, 2),
    "C#": (-3, 1),
    "D" : (-2, 2),
    "D#": (-3, 1),
    "E" : (-2, 1),
    "F" : (-1, 2),
    "F#": (-2, 1),
    "G" : (-2, 2),
    "G#": (-3, 1) }

# directory where are the samples
samples_folder = "samples"

# all samples to take.
# There is currently not the possibility to set differents notes, only differents levels
# start with the lower sample.
samples = ("ding_01.wav",
           "ding_02.wav",
           "ding_03.wav",
           "ding_04.wav",
           "ding_05.wav",
           "ding_06.wav",
           "ding_07.wav",
           "ding_08.wav",
           "ding_09.wav",
           "ding_10.wav",
           "ding_11.wav",
           "ding_12.wav")

# common properties for all regions of the instrument
in_all_groups = "loop_mode=one_shot\n" \
                + "pitch_keycenter=d3\n"

# output file names, DO NOT REMOVE ${KEY_RANGE} !!!
sfz_file = "roxang_${KEY_RANGE}minor_11"
