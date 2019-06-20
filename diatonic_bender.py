#!/usr/bin/python3

import sys

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


note_refs = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

if len(sys.argv) <= 1:
    sys.stderr.write("Please use a config file as instrument")
    sys.exit(1)
    
input_file_name = sys.argv[1]

try:
    input_file = open(input_file_name, 'r')
    input_contents = input_file.read()
    input_file.close()
except:
    sys.stderr.write("%s is not a valid file" % input_file_name)
    sys.exit(1)


key_tone = "A"
key_interval = (NoteKey("C", 0), NoteKey("G#", 9))
all_bends = {
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
samples_folder = ""
samples = []
sfz_file = ""
in_all_groups = ""

reading_in_all_groups = False

for line in input_contents.split('\n'):
    if line == "_____in_all_groups______:":
        reading_in_all_groups = True
        continue
        
    if reading_in_all_groups:
        if line == "________________________.":
            reading_in_all_groups = False
            continue
        else:
            in_all_groups += line
            in_all_groups += "\n"
    else:
        if not line:
            continue
        
        if line.startswith('#'):
            continue
        
        if line.startswith('key_tone:'):
            key_tone = line.partition('key_tone:')[2]
        elif line.startswith('key_interval:'):
            key_itv = line.partition('key_interval:')[2].split('-')
            kn_lo = makeNoteKey(key_itv[0])
            kn_hi = makeNoteKey(key_itv[1])
            
            if kn_lo and kn_hi:
                key_interval = (kn_lo, kn_hi)
            
        elif line.startswith('samples_folder:'):
            samples_folder = line.partition('samples_folder:')[2]
        elif line.startswith('sample:'):
            samples.append(line.partition('sample:')[2])
        elif line.startswith('sfz_file:'):
            sfz_file = line.partition('sfz_file:')[2]
        else:
            for note in note_refs:
                if line.partition(':')[0].replace(' ', '') == note:
                    note_contents = line.partition(':')[2]
                    bends_str = note_contents.split(',')
                    
                    try:
                        bdown = int(bends_str[0])
                        bup   = int(bends_str[1])
                    except:
                        continue
                    
                    all_bends[note] = (bdown, bup)
                    break

level_splits = []
split_n = len(samples) -1
for i in range(split_n):
    level_splits.append(int(128 * (i+1) / (split_n+1) -0.5))


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
    contents = ""
    
    for bend_group in grouped_bends:
        contents += "\n\n### bends at %s,%s ###\n" % (bend_group[0][0], bend_group[0][1])
        
        for i in range(len(level_splits)+1):
            contents += "\n<group>\n"
            contents += in_all_groups
            if not in_all_groups.endswith('\n'):
                contents += "\n"
            contents += "bend_down=%i\n" % (bend_group[0][0] * 100)
            contents += "bend_up=%i\n"   % (bend_group[0][1] * 100)
            
            if samples_folder:
                contents += "sample=%s\%s\n" % (samples_folder, samples[i])
            else:
                contents += "sample=%s\n" % samples[i]
                
            if i != 0:
                contents += "lolevel=%i\n" % (level_splits[i-1]+1)
            if i != len(level_splits):
                contents += "hilevel=%i\n" % level_splits[i]
            
            #contents += "\n"
            
            for j in range(9):
                for note in bend_group[1:]:
                    note_key = NoteKey(note, j).add(n)
                    if key_interval[0] <= note_key <= key_interval[1]:
                        contents += "<region> lokey=%s hikey=%s\n" % (note_key.toString(), note_key.toString())
    
    if "${KEY_TONE}" in sfz_file:
        file = open(sfz_file.replace("${KEY_TONE}", noteplus(key_tone, n)) + ".sfz", 'w')
        file.write(contents)
        file.close()
    else:
        file = open(sfz_file + ".sfz", 'w')
        file.write(contents)
        file.close()
        # No Key Range given, make only one file
        break
