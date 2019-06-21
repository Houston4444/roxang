#!/usr/bin/python3

import sys

READING_GENERAL = 0
READING_INSTRUMENT_OPCODES = 1
READING_INTERVAL_OPCODES = 2
READING_SAMPLE_OPCODES = 3

note_refs = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
parameters = {"KEY_TONE": "A", 
              "SAMPLES_FOLDER": "", 
              "KEY_INTERVAL": "c0-b9",
              "SAMPLE": "",
              "SAMPLE_OPCODES": "",
              "VELOCITY_SPLITS": "",
              "INTERVAL_OPCODES": "",
              "SFZ_FILE": "",
              "INSTRUMENT_OPCODES": ""}

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


class FileInterval():
    def __init__(self, lokey=NoteKey("C", 0), hikey=NoteKey("B", 9)):
        self.lokey = lokey
        self.hikey = hikey
        self.samples = []
        self.velocity_splits = []
        self.interval_opcodes = ""
        
    def addSample(self, sample):
        # self.samples is list of lists which contains [filename, opcodes] 
        self.samples.append([sample, ""])
    
    def stringInterval(self):
        return "%s-%s" % (self.lokey.toString(), self.hikey.toString())
        
    def setVelocitySplits(self, string):
        self.velocity_splits.clear()
        
        all_splits = string.split(',')
        for split in all_splits:
            try:
                int_split = int(split.replace(' ', ''))
                
                if not 0 <= int_split <= 127:
                    break
                
                self.velocity_splits.append(int_split)
            except:
                break
        
        if len(self.velocity_splits) +1 != len(self.samples):
            sys.stderr.write("Number of VELOCITY_SPLITS not coherent with number of samples\n" +
                             "will make automatic linear splits\n")
            
            self.velocity_splits.clear()
            split_n = len(self.samples) -1
            for i in range(split_n):
                self.velocity_splits.append(int(128 * (i+1) / (split_n+1) -0.5))
                
    def addIntervalOpcode(self, string):
        self.interval_opcodes += "%s\n" % string
        
    def addOpcodeToLastSample(self, opcode):
        if not self.samples:
            return False
        
        self.samples[-1][1] += "%s\n" % opcode
        return True
            

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
        
    try:
        octave = int(oct_str)
    except:
        return None
    
    return NoteKey(nnote, octave)

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
    help_contents += "\n"
    sys.stdout.write(help_contents)
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

instrument_opcodes = ""
file_intervals = []

reading = READING_GENERAL

for line in input_contents.split('\n'):
    if not line:
        reading = READING_GENERAL
        continue
    
    for param in parameters:
        if line.startswith(param + ':'):
            value = line.partition(param + ':')[2]
            reading = READING_GENERAL
            
            if param == "KEY_INTERVAL":
                key_itv = value.split(',')
                kn_lo = makeNoteKey(key_itv[0])
                kn_hi = makeNoteKey(key_itv[1])
        
                if kn_lo and kn_hi:
                    file_intervals.append(FileInterval(kn_lo, kn_hi))
                else:
                    sys.stderr.write("wrong KEY_INTERVAL, abort !\n")
                    sys.exit(1)
                 
            elif param == "SAMPLE":
                if not file_intervals:
                    file_intervals.append(FileInterval())
                file_intervals[-1].addSample(value)
                 
            elif param == "SAMPLE_OPCODES":
                if value and file_intervals:
                    file_intervals[-1].addOpcodeToLastSample(value)
                reading = READING_SAMPLE_OPCODES
            
            elif param == "VELOCITY_SPLITS":
                if file_intervals:
                    file_intervals[-1].setVelocitySplits(value)
                    
            elif param == "INTERVAL_OPCODES":
                if value and file_intervals:
                    file_intervals[-1].addIntervalOpcode(value)
                reading = READING_INTERVAL_OPCODES
            
            elif param == "INSTRUMENT_OPCODES":
                if value:
                    instrument_opcodes += value
                    instrument_opcodes += "\n"
                reading = READING_INSTRUMENT_OPCODES
            else:
                parameters[param] = value
                
            break
    else:
        if reading == READING_GENERAL:
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
            
        elif reading == READING_INSTRUMENT_OPCODES:
            instrument_opcodes += "%s\n" % line
            
        elif reading == READING_INTERVAL_OPCODES:
            if file_intervals:
                file_intervals[-1].addIntervalOpcode(line)
            
        elif reading == READING_SAMPLE_OPCODES:
            if file_intervals:
                file_intervals[-1].addOpcodeToLastSample(line)

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
    
    for file_interval in file_intervals:
        contents += "\n\n\n### interval %s ________________________________________" \
                        % file_interval.stringInterval()
                    
        for bend_group in grouped_bends:
            contents += "\n\n##### bends at %s,%s ______________________________\n" \
                            % (bend_group[0][0], bend_group[0][1])
            
            for i in range(len(file_interval.samples)):
                contents += "\n<group>\n"
                contents += instrument_opcodes
                if not instrument_opcodes.endswith('\n'):
                    contents += "\n"
                
                contents += file_interval.interval_opcodes
                
                contents += "bend_down=%i\n" % (bend_group[0][0] * 100)
                contents += "bend_up=%i\n"   % (bend_group[0][1] * 100)
                
                if parameters["SAMPLES_FOLDER"]:
                    contents += "sample=%s\%s\n" % (parameters["SAMPLES_FOLDER"], file_interval.samples[i][0])
                else:
                    contents += "sample=%s\n" % file_interval.samples[i][0]
                    
                if file_interval.samples[i][1]:
                    contents += file_interval.samples[i][1]
                    
                if i != 0:
                    contents += "lovel=%i\n" % file_interval.velocity_splits[i-1]
                if i != len(file_interval.samples) - 1:
                    contents += "hivel=%i\n" % (file_interval.velocity_splits[i] -1)
                
                for j in range(11):
                    for note in bend_group[1:]:
                        note_key = NoteKey(note, j-1).add(n)
                        if file_interval.lokey <= note_key <= file_interval.hikey:
                            key_str = note_key.toString()
                            spaces = ""
                            for i in range(4 - len(key_str)):
                                spaces += " "
                                
                            contents += "<region> lokey=%s%s hikey=%s\n" % (key_str, spaces, key_str)
    
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
