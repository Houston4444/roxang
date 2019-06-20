#!/usr/bin/python3

import sys

READING_OFF = 0
READING_COMMON_PROPERTIES = 1
READING_INTERVAL_PROPERTIES = 2
READING_SAMPLES = 3

note_refs = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
parameters = {"KEY_TONE": "A", 
              "SAMPLES_FOLDER": "", 
              "KEY_INTERVAL": "c0-b9",
              "PITCH_KEYCENTER": "c3",
              "SAMPLES": "",
              "LEVEL_SPLITS": "",
              "INTERVAL_PROPERTIES": "",
              "SFZ_FILE": "",
              "COMMON_PROPERTIES": ""}

class NoteKey():
    def __init__(self, note, octave):
        self.note = note.upper()
        self.octave = octave
        
    def __lt__(self, other):
        if self.octave < other.octave:
            return True
        if self.octave > other.octave:
            return False
        
        if self.note == other.note:
            return False
        
        for note in note_refs:
            if note == self.note:
                return True
            if note == other.note:
                return False
        else:
            return False
        
    def __eq__(self, other):
        if self.octave == other.octave and self.note == other.note:
            return True
        
        return False
    
    def __le__(self, other):
        return bool(self == other or self < other)
        
    def toString(self):
        return "%s%s" % (self.note.lower(), self.octave)
    
    def add(self, added):
        for i in range(len(note_refs)):
            if self.note.lower() == note_refs[i].lower():
                note = note_refs[(i + added) % 12]
                octave = self.octave + int((i + added)/12)
                return NoteKey(note, octave)
        else:
            raise BaseException("note %s not in note_refs")

class InputFileRange():
    def __init__(self, lokey=NoteKey("C", 0), hikey=NoteKey("B", 9)):
        self.lokey = lokey
        self.hikey = hikey
        self.samples = []
        self.pitch_keycenter = NoteKey("C", 3)
        self.level_splits = []
        self.sfz_properties = ""
    
    def setPitchKeycenter(self, note_key):
        self.pitch_keycenter = note_key
        
    def addSample(self, sample):
        self.samples.append(sample)
    
    def stringInterval(self):
        return "%s-%s" % (self.lokey.toString(), self.hikey.toString())
        
    def setLevelSplits(self, string):
        self.level_splits.clear()
        
        all_splits = string.split(',')
        for split in all_splits:
            try:
                int_split = int(split.replace(' ', ''))
                
                if not 0 <= int_split <= 127:
                    break
                
                self.level_splits.append(int_split)
            except:
                break
        
        if len(self.level_splits) +1 != len(self.samples):
            sys.stderr.write("Number of LEVEL_SPLITS not coherent with number of samples\n" +
                             "will make automatic linear splits\n")
            
            self.level_splits.clear()
            split_n = len(samples) -1
            for i in range(split_n):
                self.level_splits.append(int(128 * (i+1) / (split_n+1) -0.5))
                
    def addSfzProperty(self, string):
        self.sfz_properties += string
        self.sfz_properties += '\n'
            

        
        
def makeNoteKey(string):
    nnote   = ""
    oct_str = ""
    
    if '#' in string:
        for note in note_refs:
            if note.endswith('#') and string.upper().startswith(note):
                nnote = note
                break
        else:
            return None
        
        oct_str = string.rpartition('#')[2]
    else:
        for note in note_refs:
            if string.upper().startswith(note):
                nnote = note
                break
        else:
            return None
        
        oct_str = string[1:]
            
    if not oct_str.isdigit():
        return None
    
    return NoteKey(nnote, int(oct_str))

def noteplus(note, added):
    for i in range(len(note_refs)):
        if note.lower() == note_refs[i].lower():
            return note_refs[(i + added) % 12]
    else:
        sys.stderr.write("note %s not recognized\n" % note)
        sys.exit(1)
        
if len(sys.argv) <= 1:
    sys.stderr.write("Please use a config file as argument\n")
    sys.exit(1)

if sys.argv[1] in ('-h', '--help'):
    help_contents  = "%s is a simple script for generate SFZ instrument file with diatonic bends.\n" % sys.argv[0]
    help_contents += "Put a config file as argument to generate an instrument.\n"
    help_contents += "For example: %s Minor_11.diabd" % sys.argv[0]
    print(help_contents)
    sys.exit(0)

input_file_name = sys.argv[1]

try:
    input_file = open(input_file_name, 'r')
    input_contents = input_file.read()
    input_file.close()
except:
    sys.stderr.write("%s is not a valid file\n" % input_file_name)
    sys.exit(1)

all_bends = {
    "C" : (-1, 2),
    "C#": (-3, 1),
    "D" : (-2, 2),
    "D#": (-3, 1),
    "E" : (-2, 1),
    "F" : (-1, 2),
    "F#": (-2, 1),
    "G" : (-2, 2),
    "G#": (-3, 1),
    "A" : (-2, 2),
    "A#": (-1, 2),
    "B" : (-2, 1)}

in_all_groups = ""
input_file_ranges = []

reading = READING_OFF

for line in input_contents.split('\n'):
    if not line:
        reading = READING_OFF
        continue
    
    if reading == READING_COMMON_PROPERTIES:
        in_all_groups += line
        in_all_groups += "\n"
        
    elif reading == READING_INTERVAL_PROPERTIES:
        if input_file_ranges:
            input_file_ranges[-1].addSfzProperty(line)
        
    elif reading == READING_SAMPLES:
        if line.startswith('#'):
            continue
        
        if input_file_ranges:
            input_file_ranges[-1].addSample(line)
            
    elif reading == READING_OFF:
        if line.startswith('#'):
            continue
        
        for param in parameters:
            if line.startswith(param + ':'):
                value = line.partition(param + ':')[2]
                
                if param == "KEY_INTERVAL":
                    key_itv = value.split('-')
                    kn_lo = makeNoteKey(key_itv[0])
                    kn_hi = makeNoteKey(key_itv[1])
            
                    if kn_lo and kn_hi:
                        input_file_ranges.append(InputFileRange(kn_lo, kn_hi))
                    else:
                        sys.stderr.write("wrong KEY_INTERVAL, abort !\n")
                        sys.exit(1)
                        
                elif param == "PITCH_KEYCENTER":
                    if not input_file_ranges:
                        input_file_ranges.append(InputFileRange())
                    input_file_ranges[-1].setPitchKeycenter(makeNoteKey(value))
                        
                elif param == "SAMPLES":
                    if not input_file_ranges:
                        input_file_ranges.append(InputFileRange())
                    reading = READING_SAMPLES
                
                elif param == "LEVEL_SPLITS":
                    if input_file_ranges:
                        input_file_ranges[-1].setLevelSplits(value)
                        
                elif param == "INTERVAL_PROPERTIES":
                    reading = READING_INTERVAL_PROPERTIES
                
                elif param == "COMMON_PROPERTIES":
                    reading = READING_COMMON_PROPERTIES
                    
                else:
                    parameters[param] = value
                    
                break
        else:
            for note in note_refs:
                if line.partition(':')[0].replace(' ', '') == note:
                    note_contents = line.partition(':')[2]
                    bends_str = note_contents.split(',')
                    
                    try:
                        bdown = int(bends_str[0])
                        bup   = int(bends_str[1])
                    except:
                        sys.stderr.write("invalid bends for note %s, will take default values" % note)
                    
                    all_bends[note] = (bdown, bup)
                    break

#group bend notes
grouped_bends = []
for bend in all_bends:
    for bend_group in grouped_bends:
        if bend_group[0] == all_bends[bend]:
            bend_group.append(bend)
            break
    else:
        grouped_bends.append([all_bends[bend], bend])

# write 12 files
for n in range(12):
    contents = "# SFZ file generated by diatonic_bender.py from %s\n" % input_file_name
    
    for file_range in input_file_ranges:
        contents += "\n\n\n### interval %s ________________________________________" \
                        % file_range.stringInterval()
                    
        for bend_group in grouped_bends:
            contents += "\n\n##### bends at %s,%s ______________________________\n" \
                            % (bend_group[0][0], bend_group[0][1])
            
            for i in range(len(file_range.samples)):
                contents += "\n<group>\n"
                contents += in_all_groups
                if not in_all_groups.endswith('\n'):
                    contents += "\n"
                
                contents += file_range.sfz_properties
                
                contents += "pitch_keycenter=%s\n" % file_range.pitch_keycenter.toString()
                
                contents += "bend_down=%i\n" % (bend_group[0][0] * 100)
                contents += "bend_up=%i\n"   % (bend_group[0][1] * 100)
                
                if parameters["SAMPLES_FOLDER"]:
                    contents += "sample=%s\%s\n" % (parameters["SAMPLES_FOLDER"], file_range.samples[i])
                else:
                    contents += "sample=%s\n" % file_range.samples[i]
                    
                if i != 0:
                    contents += "lovel=%i\n" % file_range.level_splits[i-1]
                if i != len(file_range.samples) - 1:
                    contents += "hivel=%i\n" % (file_range.level_splits[i] -1)
                
                for j in range(9):
                    for note in bend_group[1:]:
                        note_key = NoteKey(note, j).add(n)
                        if file_range.lokey <= note_key <= file_range.hikey:
                            contents += "<region> lokey=%s hikey=%s\n" % (note_key.toString(), note_key.toString())
    
    if "${KEY_TONE}" in parameters["SFZ_FILE"]:
        file = open(parameters["SFZ_FILE"].replace("${KEY_TONE}", 
                                                   noteplus(parameters["KEY_TONE"], n)), 'w')
        file.write(contents)
        file.close()
    else:
        file = open(parameters["SFZ_FILE"], 'w')
        file.write(contents)
        file.close()
        # No Key Range given, make only one file
        break
