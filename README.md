diatonic_bender.py is a simple script used to generate SFZ instrument files with diatonic bends.<br>
With it, bends made with the pitch wheel can stay in the key tone.<br>
For example: with an instrument with pitchs at -1tone +1tone in A minor,<br>
an upped A will gives a B (2semitones), but an upped E will give a F (one semitone).
So, a bent up G chord will give an Aminor, a bent down G will gives a F.

To make a new instrument just copy/edit a given .diabd file and run:<br>
`./diatonic_bender my_file.diabd`<br>
replace "my_file.diabd" with your file name, of course !<br>

On some systems you'll have to type instead:<br>
`python3 diatonic_bender my_file.diabd`<br>

