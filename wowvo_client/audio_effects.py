from pydub import AudioSegment
import subprocess, os
import librosa
import soundfile as sf


def dk_effects(mp3_path, voice_key):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"

    subprocess.run([
        'sox', working_path, changed,
        'bass', '10',
        'tremolo', '200',
        'reverb', '50', '50', '75', '100', '25', '-5',
        'gain', '3',
        'gain', '-n'], check=True)

    working_path = changed


    y, sr = librosa.load(working_path, sr=None)
    processed = librosa.effects.pitch_shift(y=y, sr=sr,
                        n_steps=-2.75 if voice_key in ('vrykul_male_dk','mountain_giant_dk','troll_female_dk','giant_female_dk') else -4 if voice_key in ('naga_male_dk') else -0.5) #raspy voice

    # Save processed audio to temp wav file
    temp_final_wav = base_path + "_final.wav"
    sf.write(temp_final_wav, processed, sr)

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(temp_final_wav)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def robot_effects(mp3_path):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run(['sox', working_path, changed,
                    'tremolo', '100000',
                    'pitch', '-250',
                    'lowpass', '4000',      # Remove high frequencies
                    'gain', '-n',], check=True)
    working_path = changed


    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def ghost_effects(mp3_path, voice):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    if voice in ('banshee'):
        effect = 'voices/_effects/banshee.wav'
        duration = subprocess.check_output(['soxi', '-D', mp3_path]).decode().strip()
        temp_effect = effect + "_temp_loop.wav"
        subprocess.run([
            'sox', effect, temp_effect,
            'repeat', '100', 'trim', '0', duration
        ], check=True)

        subprocess.run([
            'sox', '-m',
            '-v', '1.0', working_path,
            '-v', '0.35', temp_effect, # Adjust volume here
            changed,
            'pitch', '-100',
            'reverb', '100', '70', '50', '80', '50', '0',
            'gain','-n',
        ], check=True)
        os.remove(temp_effect)
    else:
        subprocess.run([
            'sox', working_path, changed,
            'reverb', '100', '70', '50', '80', '50', '0',
            'gain','-n',
        ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def undead_effects(mp3_path):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
        'sox', working_path, changed,
        'reverb', '15', '35', '30', '10', '60', '-3'
    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def demon_effects(mp3_path, voice_key):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension
    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")
    changed = base_path + "_changed.wav"

    if voice_key in ('dragon_male','dragon_female'):
        print('for dragon...', flush=True)
        dragon = 'voices/_effects/dragon.wav'
        duration = subprocess.check_output(['soxi', '-D', mp3_path]).decode().strip()
        temp_dragon = dragon + "_temp_loop.wav"
        subprocess.run([
            'sox', dragon, temp_dragon,
            'repeat', '100', 'trim', '0', duration
        ], check=True)

        subprocess.run([
            'sox', '-m',
            '-v', '1.0', working_path,
            '-v', '0.20', temp_dragon, # Adjust volume here
            changed,
            'pitch', '-100',
            'reverb', '32', '40', '40', '50', '25', '-5',
            'gain','-n',
        ], check=True)
        os.remove(temp_dragon)
    elif voice_key in ('fire_elemental','water_elemental',"earth_elemental","wind_elemental"):
        if voice_key == 'fire_elemental':
            effect = 'voices/_effects/fire.wav'
        elif voice_key == 'earth_elemental':
            effect = 'voices/_effects/earth.wav'
        elif voice_key == 'wind_elemental':
            effect = 'voices/_effects/wind.wav'
        elif voice_key == 'water_elemental':
            effect = 'voices/_effects/water.wav'
        duration = subprocess.check_output(['soxi', '-D', mp3_path]).decode().strip()
        temp_effect = effect + "_temp_loop.wav"

        subprocess.run([
            'sox', effect, temp_effect,
            'repeat', '100', 'trim', '0', duration
        ], check=True)

        subprocess.run([
            'sox', '-m',
            '-v', '1.0', working_path,
            '-v', '0.35', temp_effect, # Adjust volume here
            changed,
            'pitch', '-100',
            'reverb', '32', '40', '40', '50', '25', '-5',
            'gain','-n',
        ], check=True)
        os.remove(temp_effect)
    elif voice_key in ('demon_male', 'demon_female','bone_witch','sanlayn'):
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-100',
            'echo', '0.8', '0.85', '150', '0.3',
            'reverb', '30', '100', '20', '1', '100', '-5',
            'gain','-n',
        ], check=True)
    elif voice_key in ('abomination'):
        print("abomination effects...", flush = True)
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-250',
            #'echo', '0.8', '0.85', '50', '0.5','100','0.3','25', '0.6','75','0.4', four echoes sound metallic almost like dk effects from the game
            'chorus', '0.5', '0.8', '40', '0.3', '0.25', '2', '-t',
            'reverb', '15', '35', '20', '1', '80', '-3',
            'gain','3',
            'gain','-n',
        ], check=True)
    elif voice_key in ('akama'):
        print("abomination effects...", flush = True)
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-250',
            'reverb', '15', '35', '20', '1', '80', '-5',
            'gain','3',
            'gain','-n',
        ], check=True)
    else:
        print("general demon effects...", flush = True)
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-100',
            'reverb', '30', '100', '20', '1', '80', '-5',
            'gain','-n',
        ], check=True)
    working_path = changed
    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def ethereal_effects(mp3_path, voice_key):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    if voice_key in ('ethereal_male'):
        subprocess.run([
            'sox', working_path, changed,
            'echo', '0.8', '0.85', '125', '0.25',
            'reverb', '50', '60', '100', '100', '100', '-4',
            'gain','5',
        ], check=True)
    elif voice_key in ('ethereal_stalker'):
        subprocess.run([
            'sox', working_path, changed,
            'pitch','-125',
            'bass', '10',
            'echo', '0.8', '0.85', '125', '0.25',
            'reverb', '50', '60', '100', '100', '100', '-4',
            'gain','7',
        ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def giant_effects(mp3_path, voice):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    if voice in (["ogrila_ogre"]):
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-350',
            'tempo', '0.85',
            'gain','-n',
        ], check=True)
    elif voice in (['ogre_male']):
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-200',
            'tempo', '0.90',
            'gain','-n',
        ], check=True)
    elif voice in (['ancient', 'mountain_giant']):
        print("Ancient effects...", flush = True)
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-220',
            'reverb', '43', '40', '40', '50', '25', '-4',
            'gain','-n',

        ], check=True)
    elif voice in ('giant_male','giant_female'):
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-125',
            'bass','+8',
            'reverb', '43', '40', '40', '50', '25', '-4',
            'tempo', '1.2',
        ], check=True)
    elif voice in ('cairne'):
        subprocess.run([
            'sox', working_path, changed,
            'tempo', '1.2',
        ], check=True)
    else:
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-100',
            'tempo', '1.2',
        ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))
def small_effects(mp3_path, voice):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    if voice in ('gorloc_male'):
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '275',
            'chorus', '0.5', '0.8', '40', '0.3', '0.25', '2', '-t',
            'gain', '-n'

        ], check=True)
    elif voice in ('wolvar_male'):
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '200',
            'reverb', '32', '40', '40', '50', '25', '-8',
            'gain', '-n'

        ], check=True)
    elif voice in ('gnome_female'):
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '25',
            'gain', '-n'

        ], check=True)
    elif voice in ('girl'):
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '75',
            'gain', '-n'

        ], check=True)
    elif voice in ('geist'):
        subprocess.run([
            'sox', working_path, changed,
            'chorus', '0.5', '0.8', '40', '0.3', '0.25', '2', '-t',
            'gain', '-n'

        ], check=True)
    else:
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '350',
            'gain', '-n'

        ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def earthen_effects(mp3_path):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
       'sox', working_path, changed,
       'pitch', '-25',
       'gain', '2',
    ], check=True)
    working_path = changed

    y, sr = librosa.load(working_path, sr=None)
    processed = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=-1.50) #for raspy voice

    # Save processed audio to temp wav file
    temp_final_wav = base_path + "_final.wav"
    sf.write(temp_final_wav, processed, sr)

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(temp_final_wav)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def naaru_effects(mp3_path):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    print(base_path)
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
       'sox', working_path, changed,
       'pitch', '-150',
       'tremolo','100',
       'reverb', '60', '50', '60', '100', '50', '-5',
       'gain', '-n',

    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate = "64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def comms_effects(mp3_path):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3

    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
       'sox', working_path, changed,
       'highpass', '300',
       'lowpass','3400',

    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate = "64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))
def underwater_effects(mp3_path):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
       'sox', working_path, changed,
       'lowpass', '3200',
       'flanger', '0', '5', '10', '80', '0.3', 'sine', '50', 'quadratic',

    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate = "64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def bubble_effects(mp3_path):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    #bubbles
    bubbles = 'voices/_effects/bubbles.wav'
    duration = subprocess.check_output(['soxi', '-D', mp3_path]).decode().strip()

    # Work in-place using temporary intermediate files with .wav extension
    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    print(base_path)

    temp_bubbles = bubbles + "_temp_loop.wav"
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"

    #loop effect x100 to make sure it's as long as mp3_path
    subprocess.run([
        'sox', bubbles, temp_bubbles,
        'repeat', '100', 'trim', '0', duration
    ], check=True)

    #Mix the voice with that temporary loop
    subprocess.run([
        'sox', '-m',
        '-v', '1.0', working_path,
        '-v', '0.5', temp_bubbles, # Adjust volume here
        changed
    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate = "64k")

    # Clean up temp wavs
    os.remove(temp_bubbles)
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def beast_effects(mp3_path, voice_key):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension
    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")
    changed = base_path + "_changed.wav"

    if voice_key in ('wolf'):
        effect = 'voices/_effects/wolf.wav'
    elif voice_key in ('bear'):
        effect = 'voices/_effects/bear.wav'
    elif voice_key in ('cat'):
        effect = 'voices/_effects/cat.wav'
    elif voice_key in ('serpent'):
        effect = 'voices/_effects/serpent.wav'
    elif voice_key in ('mammoth'):
        effect = 'voices/_effects/mammoth.wav'
    duration = subprocess.check_output(['soxi', '-D', mp3_path]).decode().strip()
    temp_effect = effect + "_temp_loop.wav"

    subprocess.run([
        'sox', effect, temp_effect,
        'repeat', '100', 'trim', '0', duration
    ], check=True)

    subprocess.run([
        'sox', '-m',
        '-v', '1.0', working_path,
        '-v', '0.30', temp_effect, # Adjust volume here
        changed,
        'pitch', '-100',
        'reverb', '32', '40', '40', '50', '25', '-8',
        'gain','-n',
    ], check=True)
    os.remove(temp_effect)
    working_path = changed
    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))
