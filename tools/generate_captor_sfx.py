"""Retained-original Captor foley pack generated using ElevenLabs."""
from generate_engineer_impact_sfx import generate
CLIPS=[
('captor_bola','Single close fantasy weighted bola throw: soft fast rope swish and spinning cord, then three dull leather wrapped metal weights catch and cinch tight. Compact natural foley. No music, voices, shrill metallic ring or magic.',1.0),
('captor_drag','Single close fantasy chain hook pulling: quick low chain rustle, solid hook catch, then taut rope and chain dragged across earth. Short weighty friction, no voices, music or sharp ringing.',1.0),
('captor_hold','Single close restraint tightening: thick rope creaking under pressure, leather glove grip and short dull padded impact. A firm cinch, dry and grounded. No voices, music, bone crunch or ringing.',.8),
('captor_blitz','Single agile pursuit preparation: boot scuff and two quick grounded running footfalls, low rushing cloth movement. Confident compact ready cue, no voices music magic or ringing.',.8)]
if __name__=='__main__':
 for name,prompt,duration in CLIPS:generate(name,prompt,duration,'captor-v1/'+name)
