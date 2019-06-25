diatonic_bender.py is a simple script used to generate SFZ instrument files with diatonic bends.<br>
With it, bends made with the pitch wheel of a MIDI keyboard can stay in the key tone.<br>
For example: with an instrument with pitchs at -1tone +1tone in A minor,<br>
a bent up A will gives a B (2semitones), but a bent up E will give a F (one semitone).
So, a bent up G chord will give an Aminor, a bent down G will gives a F.

Important: This feature wont works with LinuxSampler, but it works with Carla Plugin Host!<br>
Just drag and drop your *.sfz file to Carla window.<br>

To make a new instrument just copy/edit a given *.diabd file and run in terminal:<br>
`./diatonic_bender my_file.diabd`<br>
replace "my_file.diabd" with your file name, of course !<br>

On some systems you'll have to type instead:<br>
`python3 diatonic_bender my_file.diabd`<br>


-- EN FRANÇAIS --

diatonic_bender.py est un simple script qui permet de générer des instruments au format SFZ avec des bends diatoniques.<br>
Avec ceci, les notes bendés par la molette de pitch d'un clavier MIDI peuvent rester dans la gamme.<br>
Par exemple: Sur un instrument avec les pitchs à -1 ton, + 1 ton en La mineur,<br>
un La modulé vers le haut donnera un Si (+2 demi-tons), alors qu'un Mi donnera un Fa (+1 demi-ton).<br>
Du coup, un accord de SOL modulé vers le haut donnera un LA mineur, modulé vers le bas il donnera un FA.<br>

Important: Ceci ne fonctionnera pas avec LinuxSampler, mais ça marche avec Carla !<br>
Glissez/Déposez votre fichier *.sfz jusqu'à la fenêtre de Carla.<br>

Pour générer un nouvel instrument, copiez/editez un ficher en *.diabd fourni et lancez via le terminal:<br>
`./diatonic_bender mon_fichier.diabd`<br>
Remplacez "mon_fichier.diabd" par le nom du fichier utilisé, ça va de soit!<br>

Sur certains systèmes vous devrez tapez à la place:<br>
`python3 diatonic_bender mon_fichier.diabd`<br>
