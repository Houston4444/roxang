#!/usr/bin/python3

import os
import sys

READING_GENERAL            = 0
READING_INSTRUMENT_BENDS   = 1
READING_INSTRUMENT_OPCODES = 2
READING_INTERVAL_BENDS     = 3
READING_INTERVAL_OPCODES   = 4
READING_SAMPLE_OPCODES     = 5

FILE_EXISTS_ASK     = 0
FILE_EXISTS_ABORT   = 1
FILE_EXISTS_ERASE   = 2
FILE_EXISTS_ENQUEUE = 3

note_refs = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
parameters = {"KEY_TONE": "A",
              "INSTRUMENT_BENDS": "",
              "ONE_CHANNEL_PER_TONE": "false",
              "SFZ_FILE": "",
              "SAMPLES_FOLDER": "", 
              "KEY_INTERVAL": "c-1,g9",
              "SAMPLE": "",
              "SAMPLE_OPCODES": "",
              "VELOCITY_SPLITS": "",
              "INTERVAL_OPCODES": "",
              "INSTRUMENT_OPCODES": "",
              "INTERVAL_BENDS": ""}


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


class Sample():
    opcodes = ""
    lovel = 0
    hivel = 127
    
    def __init__(self, filename):
        self.filename = filename
        
    def addOpcode(self, opcode):
        self.opcodes += "%s\n" % opcode
        
    def getAllContents(self):
        contents = ""
        
        if parameters["SAMPLES_FOLDER"]:
            contents += "sample=%s\%s\n" % (parameters["SAMPLES_FOLDER"], self.filename)
        else:
            contents += "sample=%s\n" % self.filename
            
        if self.opcodes:
            contents += self.opcodes
            
        contents += "lovel=%i\n" % self.lovel
        contents += "hivel=%i\n" % self.hivel
        
        return contents


class FileInterval():
    def __init__(self, lokey=NoteKey("C", -1), hikey=NoteKey("G", 9)):
        self.lokey = lokey
        self.hikey = hikey
        self.samples = []
        self.interval_opcodes = ""
        self.splits_done = False
        self.bends = instrument_bends.copy()
        
    def addSample(self, filename):
        sample = Sample(filename)
        self.samples.append(sample)
    
    def stringInterval(self):
        return "%s;%s" % (self.lokey.toString(), self.hikey.toString())
        
    def setVelocitySplits(self, string=''):
        velocity_splits = [0]
        
        all_splits = string.split(',')
        for split in all_splits:
            try:
                int_split = int(split.replace(' ', ''))
                
                if not 0 < int_split < 127:
                    continue
                
                velocity_splits.append(int_split)
            except:
                break
        
        velocity_splits.append(128)
        velocity_splits.sort()
        
        if len(velocity_splits) != len(self.samples) +1:
            sys.stderr.write("Number of VELOCITY_SPLITS not coherent with number of samples\n" +
                             "will make automatic linear splits\n")
            
            velocity_splits = [0]
            
            split_n = len(self.samples) -1
            for i in range(split_n):
                velocity_splits.append(int(128 * (i+1) / (split_n+1) -0.5))
                
            velocity_splits.append(128)
        
        for i in range(len(self.samples)):
            self.samples[i].lovel = velocity_splits[i] 
            self.samples[i].hivel = velocity_splits[i+1] -1
        
        self.splits_done = True
                
    def addIntervalOpcode(self, string):
        self.interval_opcodes += "%s\n" % string
        
    def addOpcodeToLastSample(self, opcode):
        if not self.samples:
            return False
        
        self.samples[-1].addOpcode(opcode)
        return True
    
    def setBend(self, note, bend_down, bend_up):
        self.bends[note] = (bend_down, bend_up)
        
    def getAllContents(self, toneplus=0, channel=0):
        if not self.splits_done:
            self.setVelocitySplits()
        
        grouped_bends = []
        
        for bend in self.bends:
            for bend_group in grouped_bends:
                if bend_group[0] == self.bends[bend]:
                    bend_group.append(bend)
                    break
            else:
                grouped_bends.append([self.bends[bend], bend])
        
        contents = "\n\n\n### interval %s;%s ________________________________________" \
                        % (self.lokey.toString(), self.hikey.toString())
                    
        for bend_group in grouped_bends:
            contents += "\n\n##### bends at %s,%s ______________________________\n" \
                            % (bend_group[0][0], bend_group[0][1])
            
            for sample in self.samples:
                contents += "\n<group>\n"
                contents += instrument_opcodes
                if not instrument_opcodes.endswith('\n'):
                    contents += "\n"
                
                if channel:
                    contents += "lochan=%i hichan=%i\n" % (channel, channel)
                
                contents += self.interval_opcodes
                
                contents += "bend_down=%i\n" % (bend_group[0][0] * 100)
                contents += "bend_up=%i\n"   % (bend_group[0][1] * 100)
                
                contents += sample.getAllContents()
                
                for i in range(11):
                    for note in bend_group[1:]:
                        note_key = NoteKey(note, i-1).add(toneplus)
                        if self.lokey <= note_key <= self.hikey:
                            key_str = note_key.toString()
                            
                            # just for alignment
                            spaces = ""
                            for j in range(4 - len(key_str)):
                                spaces += " "
                                
                            contents += "<region> lokey=%s%s hikey=%s\n" % (key_str, spaces, key_str)
        
        return contents
        
            

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

def keyTonePlus(added):
    tone_note = NoteKey(parameters['KEY_TONE'], 0)
    added_note = tone_note.add(added)
    return added_note.note

def writeSfzFile(contents, toneplus=0):
    global file_exists_behaviour
    
    tone = parameters['KEY_TONE']
    if toneplus:
        tone = keyTonePlus(toneplus)
        
    sfz_file = parameters['SFZ_FILE'].replace('${KEY_TONE}', tone)
        
    if file_exists_behaviour == FILE_EXISTS_ASK and os.path.exists(sfz_file):
        question = "%s already exists.\n" % sfz_file
        question+= "Type Q to abort, E to erase existing file,\n"
        question+= "or W to write at the the end of the existing file:"

        sys.stdout.write(question)
        answer = sys.stdin.readline().replace('\n', '')
        
        if answer.upper() == "W":
            file_exists_behaviour = FILE_EXISTS_ENQUEUE
            sys.stderr.write("Enqueue in files\n")
        elif answer.upper() == "E":
            file_exists_behaviour = FILE_EXISTS_ERASE
            sys.stderr.write("Erase Files\n")
        else:
            file_exists_behaviour = FILE_EXISTS_ABORT
            sys.stdout.write('Abort.\n')
            sys.exit(0)
    
    elif file_exists_behaviour == FILE_EXISTS_ENQUEUE:
        try:
            file = open(sfz_file, 'r')
            primo_contents = file.read()
            file.close()
        except:
            sys.stderr.write("read error, %s not written\n" % sfz_file)
            return
        
        contents = "%s\n%s" % (primo_contents, contents)
    
    sys.stdout.write("%s\n" % sfz_file)
    
    try:
        file = open(sfz_file, 'w')
        file.write(contents)
        file.close()
    except:
        sys.stderr.write("write error for %s\n" % sfz_file)
        
    

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.stderr.write("Please use a config file as argument\n")
        sys.exit(1)

    args = sys.argv[1:]
    input_file_name = args[0]
    file_exists_behaviour = FILE_EXISTS_ASK
    
    if args[0] in ('-h', '--help'):
        help_contents  = "%s is a simple script for generate SFZ instrument file with diatonic bends.\n" % sys.argv[0]
        help_contents += "Usage: %s [option] input_file : Make SFZ file from input file.\n" % sys.argv[0]
        help_contents += "  -h, --help  Display this help and exit\n"
        help_contents += "  -e          if SFZ file already exists, erase it\n"
        help_contents += "  -w          if SFZ file already exists, write at the end of file\n"
        sys.stdout.write(help_contents)
        sys.exit(0)
    
    elif args[0] in ('-e', '-w'):
        if len(args) < 2:
            sys.stderr.write("Please use a config file as argument\n")
            sys.exit(1)
        
        if args[0] == '-e':
            file_exists_behaviour = FILE_EXISTS_ERASE
        elif args[0] == '-w':
            file_exists_behaviour = FILE_EXISTS_ENQUEUE
            
        input_file_name = args[1]
        

    try:
        input_file = open(input_file_name, 'r')
        input_contents = input_file.read()
        input_file.close()
    except:
        sys.stderr.write("%s is not a valid file\n" % input_file_name)
        sys.exit(1)

    instrument_bends = {
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

    # read the config file
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
                
                elif param == "INSTRUMENT_BENDS":
                    reading = READING_INSTRUMENT_BENDS
                
                elif param == "INTERVAL_BENDS":
                    reading = READING_INTERVAL_BENDS
                
                elif param == "INSTRUMENT_OPCODES":
                    if value:
                        instrument_opcodes += value
                        instrument_opcodes += "\n"
                    reading = READING_INSTRUMENT_OPCODES
                        
                else:
                    parameters[param] = value
                    
                break
        else:
            if reading in (READING_INSTRUMENT_BENDS, READING_INTERVAL_BENDS):
                for note in note_refs:
                    if line.partition(':')[0].replace(' ', '') == note:
                        note_contents = line.partition(':')[2]
                        bends_str = note_contents.split(',')
                        
                        try:
                            bdown = int(bends_str[0])
                            bup   = int(bends_str[1])
                        except:
                            sys.stderr.write("invalid bends for note %s, will take default values" % note)
                        
                        if reading == READING_INSTRUMENT_BENDS:
                            instrument_bends[note] = (bdown, bup)
                        elif reading == READING_INTERVAL_BENDS:
                            if file_intervals:
                                file_intervals[-1].setBend(note, bdown, bup)
                        break
                
            elif reading == READING_INSTRUMENT_OPCODES:
                instrument_opcodes += "%s\n" % line
                
            elif reading == READING_INTERVAL_OPCODES:
                if file_intervals:
                    file_intervals[-1].addIntervalOpcode(line)
                
            elif reading == READING_SAMPLE_OPCODES:
                if file_intervals:
                    file_intervals[-1].addOpcodeToLastSample(line)
                
                
    if not parameters['SFZ_FILE']:
        sys.stderr.write("No SFZ_FILE specified. Abort.\n")
        sys.exit(1)
        
    one_channel_per_tone = bool(parameters['ONE_CHANNEL_PER_TONE'] == "true")

    contents = ""
    
    # write 12 files (one per key tone)
    for n in range(12):
        contents = "# SFZ file generated by diatonic_bender.py from %s\n" % input_file_name
        
        if one_channel_per_tone:
            # write 12 channels
            for i in range(12):
                contents += "\n\n## Tone %s, channel %i ___________________________________________\n" % \
                                (keyTonePlus(n+i), i+1)
                for file_interval in file_intervals:
                    contents += file_interval.getAllContents(n+i, i+1)
        else:
            for file_interval in file_intervals:
                contents += file_interval.getAllContents(n)
        
        if "${KEY_TONE}" in parameters["SFZ_FILE"]:
            writeSfzFile(contents, n)
        else:
            writeSfzFile(contents)
            # No Key Range given, make only one file
            break
    

    ## write 12 files or 12 channels (one per key tone)
    #for n in range(12):
        #if n == 0 or not one_channel_per_tone:
            #contents = "# SFZ file generated by diatonic_bender.py from %s\n" % input_file_name
        
        #if one_channel_per_tone:
            #contents += "\n\n## Tone %s, channel %i ___________________________________________\n" % (keyTonePlus(n), n+1)
        
        #for file_interval in file_intervals:
            #contents += file_interval.getAllContents(n)
        
        #if one_channel_per_tone:
            #if n == 11:
                #writeSfzFile(contents)
            #else:
                #continue
        #elif "${KEY_TONE}" in parameters["SFZ_FILE"]:
            #writeSfzFile(contents, n)
        #else:
            #writeSfzFile(contents)
            ## No Key Range given, make only one file
            #break
