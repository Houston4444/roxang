#!/usr/bin/python3

from edit_me import *





##### Script start, should not edit after this ##### 

note_refs = ("A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#")

def noteplus(note, added):
    for i in range(len(note_refs)):
        if note.lower() == note_refs[i].lower():
            return note_refs[(i + added) % 12]
    else:
        print("note %s not recognized" % note)
        sys.exit(1)
            

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
                contents += "sample=%s\n" % (samples_folder, samples[i])
                
            if i != 0:
                contents += "lolevel=%i\n" % (level_splits[i-1]+1)
            if i != len(level_splits):
                contents += "hilevel=%i\n" % level_splits[i]
            
            #contents += "\n"
            
            for j in range(9):
                for note in bend_group[1:]:
                    nnote = noteplus(note, n).lower()
                    print(n, note, nnote)
                    contents += "<region> lokey=%s%i hikey=%s%i\n" % (nnote, j, nnote, j)
                    

    file = open(sfz_file.replace("${KEY_RANGE}", noteplus(key_range, n)) + ".sfz", 'w')
    file.write(contents)
    file.close()
