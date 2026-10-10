"""Generate compact physical specialty cues; reuse every retained original."""
from generate_engineer_impact_sfx import generate

CLIPS={
 'tripline_set':('Short taut hemp rope pulled tight between wooden stakes, two muted wooden taps and a rope tension creak. Dry close physical game foley, no music, no speech, no magic, no shrill ringing.',.8),
 'tripline_snap':('One hemp tripwire abruptly snapping with a dry twang, rope whipping loose and a stumbling boot scraping dirt. Short earthy contact, no music, no speech, no metallic ringing.',.7),
 'shakedown':('A single forceful cudgel strike against a padded body: deep heavy flesh thump and short grunt-like breath of impact, bone weight, no spoken voice, no metallic clang, no music, dry short decay.',.7),
 'parting_cut':('One close short wet dagger slice into flesh, followed by a quick leather boot scraping backward on dirt. Quiet blade movement, strong soft wet contact. No metal clang, no ringing, no music or speech.',.8),
 'ankle_bite':('One low close blade cut through leather into flesh with a sharp wet slice and brief boot buckle rattle. Grounded compact physical impact, no ringing metal, music or speech.',.65),
 'goliath_shot':('A heavy sling stone thuds hard against a helmet with a short dull iron knock and gritty stone fragments. Weighty compact hit, not a sword clang, no shrill ringing, music or speech.',.8),
 'tag_team':('Two quick leather boot scuffs crossing in opposite directions with soft cloth swishes, ending with a short solid body bump. Fast tactical maneuver, no teleport magic, no music or speech.',.8),
 'heel_cut':('Close wet blade slice through a boot heel into flesh, brief sharp contact followed by small wet drops. Dark compact grounded game impact, no metallic clang, music or speech.',.7),
 'cornered_fury':('Short forceful nonverbal exhale with a deep heavy leather and weapon movement rush, a grounded furious fighter preparing a wide swing. No words, no music, no magical hum or ringing.',.7),
}
if __name__=='__main__':
    for name,(prompt,duration) in CLIPS.items():generate('specialty_'+name,prompt,duration,'enemy-specialties-v1')
