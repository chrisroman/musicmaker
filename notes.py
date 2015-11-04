from random import randint
from MidiFile3 import *

class Scale :
  # Contains all 12 possible notes
  notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
  
  # [C D E F G A B C]
  # CEG, DFA, EGB, FAC, 
  def __init__(self, root_note, tonality):
    self.root_note = root_note # Key of the melody
    self.root_pos = Scale.notes.index(root_note) # Position required to create the scale
    self.keys = [root_note] # Holds all keys of the scale
    self.tonality = tonality # Either Major or Minor
    self.major_intervals = [2, 2, 1, 2, 2, 2, 1] # Number of steps to go up in a major/minor scale
    self.minor_intervals = [2, 1, 2, 2, 1, 3, 1]
    if self.tonality == "major" :
      curr_pos = self.root_pos
      for i in range(len(self.major_intervals)) : # Add to the root position and take the note at that position(mod12 because it needs to loop over)
        curr_pos += self.major_intervals[i]
        curr_pos = curr_pos % 12
        self.keys.append(Scale.notes[curr_pos])
    elif self.tonality == "minor" :
      curr_pos = self.root_pos
      for i in range(len(self.minor_intervals)) :
        curr_pos += self.minor_intervals[i]
        curr_pos = curr_pos % 12
        self.keys.append(Scale.notes[curr_pos])
    self.chords = self.makeChords() # Create all the chords for the respective scale

  def getKeys(self) :
    return self.keys
  def getRootNote(self) :
    return self.root_note
  def getTonality(self):
    return self.tonality
  def getChords(self) :
    return self.chords

  def printChords(self) :
    for thing in self.chords :
      print(thing)

  # [C, D, E, F, G, A, B, C]
  def makeChords(self) :
    chords = []
    for i in range(len(self.keys) - 1) :
      localChord = [self.keys[i%7], self.keys[(i + 2)%7], self.keys[(i + 4)%7]]
      chords.append(localChord)
    return chords

  def findTriads(self, note) :
    triads = []
    for chord in self.chords :
      if note in chord :
        triads.append(chord)
    return triads

  def __str__(self) :
    return "%s %s: %s" %(self.root_note, self.tonality, str(self.keys))

class FourPartHarmony :
  def __init__(self, s, a, t, b) :
    self.soprano = s
    self.alto = a
    self.tenor = t
    self.bass = b
    self.harmony = [s, a, t, b]

  def getHarmony(self) :
    return self.harmony

  def __repr__(self) :
    return "[%s, %s, %s, %s]" %(self.soprano, self.alto, self.tenor, self.bass)

class MeasuresMaker:
  def __init__(self, scale, melody):
    self.measure = []
    self.beats = 4
    self.melody = melody
    self.scale = scale
    self.melodize()
    self.length = 0
  
  def getMeasure(self) :
    return self.measure

  def melodize(self) :
    localMeasure = []
    for i in range(len(self.melody)) :
      localMeasure.append(self.harmonize(self.melody[i]))
      if i % self.beats == 3 and i != 0 :
        self.measure += localMeasure
        localMeasure = []
    if len(localMeasure) != 0 :
      self.measure += localMeasure
    self.length = len(self.measure)

  def harmonize(self, m_note) :
    soprano = m_note
    triads = self.scale.findTriads(m_note)
    rand_triad = triads[randint(0, len(triads)) - 1]
    helper = [rand_triad[0], rand_triad[1], rand_triad[2]]
    temp = ["a", "t", "b"] # Placeholders
    for i in range(3) :
      rand_index = randint(0, len(helper) - 1)
      temp[i] = helper.pop(rand_index)
    alto = temp[0]
    tenor = temp[1]
    bass = temp[2] # [C E G].pop(1) => E... list is now: [C G].pop()

    return FourPartHarmony(soprano, alto, tenor, bass)

  def __str__(self) :
    for thing in self.measure :
      print(thing)
    return ""

class Composer:
  def __init__(self, scale, tune) :
    self.octave = dict([('C',60),('D',62),('E',64),('F',65),
                        ('G',67),('A',69),('B',71),
                        ('C#',61),('D#',63),('F#',66),('G#',68),('A#',70),
                        ('Db',61),('Eb',63),('Gb',66),('Ab',68),('Bb',70)])
    self.song = MeasuresMaker(scale, tune)
    self.midi_file = MIDIFile(4)
    self.tracks = (0, 1, 2, 3)
    self.start_time = 0
    self.channels = (0, 1, 2, 3)
    self.volume = 100
    self.soprano_start = self.start_time
    self.alto_start = self.start_time
    self.tenor_start = self.start_time
    self.bass_start = self.start_time

  def setBPM(self, bpm) :
    self.midi_file.addTempo(self.tracks[0], self.start_time, bpm)

  def playMelody(self, note, time) :
    self.midi_file.addNote(self.tracks[0], self.channels[0], note + 12, self.soprano_start, time, int(self.volume))
    self.soprano_start += time
  def playAlto(self, vol, note, time) :
    self.midi_file.addNote(self.tracks[0], self.channels[1], note + 12, self.alto_start, time, int(vol))
    self.alto_start += time
  def playTenor(self, vol, note, time) :
    self.midi_file.addNote(self.tracks[0], self.channels[2], note, self.tenor_start, time, int(vol))
    self.tenor_start += time
  def playBass(self, vol, note, time) :
    self.midi_file.addNote(self.tracks[0], self.channels[3], note - 12, self.bass_start, time, int(vol))
    self.bass_start += time

  def playSong(self) :
    length = len(self.song.getMeasure())
    measure = self.song.getMeasure()
    for i in range(length) :
      # Have the soprano play whatever they want
      biasChoice = [.25, .25, .5, .5, .5, 1, 1]
      someRand = biasChoice[randint(0, len(biasChoice)) - 1]
      harm = self.song.getMeasure()[i].getHarmony()
      try :
        nextHarm = self.song.getMeasure()[i+1].getHarmony()
      except :
        pass
      sop = self.octave[harm[0]]
      self.playMelody(sop, someRand)
      if someRand == .5 :
        self.playMelody(self.octave[nextHarm[0]], someRand)

      # Only harmonize if "lucky"
      chance = randint(0, 100) < 35
      alto  = self.octave[harm[1]]
      tenor = self.octave[harm[2]]
      bass  = self.octave[harm[3]]
      if chance :
        self.playAlto(self.volume, alto, someRand)
        self.playTenor(self.volume, tenor, someRand)
        self.playBass(self.volume, bass, someRand)
        if someRand == .5 :
          self.playAlto(self.volume, self.octave[nextHarm[1]], someRand)
          self.playTenor(self.volume, self.octave[nextHarm[2]], someRand)
          self.playBass(self.volume, self.octave[nextHarm[3]], someRand)
          i += 1
      else :
        self.playAlto(0, sop - 12, someRand)
        self.playTenor(0, sop, someRand)
        self.playBass(0, sop + 12, someRand)
        if someRand == .5 :
          self.playAlto(self.volume, self.octave[nextHarm[1]], someRand)
          self.playTenor(self.volume, self.octave[nextHarm[2]], someRand)
          self.playBass(self.volume, self.octave[nextHarm[3]], someRand)
          i += 1

  def makeFile(self) :
    binfile = open("test.mid", 'wb')
    self.midi_file.writeFile(binfile)
    binfile.close()


# -------------------------------------------------------------
scale = Scale("E", "major")
print("Please enter notes from the following scale: %s" %(str(scale)))
melody = []
for i in range(100) :
  melody.append(scale.getKeys()[randint(0, 7)])
measure = MeasuresMaker(scale, melody)

mydy = Composer(scale, melody)
mydy.setBPM(100)
mydy.playSong()
mydy.makeFile()