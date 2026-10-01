import unittest
from PIL import Image,ImageDraw
from tools.audit_catalogue_crops import source_icons,recovered_icon

class CatalogueCropTests(unittest.TestCase):
    def test_recovery_retains_full_silhouette_and_excludes_neighbor(self):
        source=Image.new('RGBA',(320,180));draw=ImageDraw.Draw(source)
        draw.rectangle((20,20,170,140),fill=(255,255,255,255))
        draw.rectangle((177,30,305,150),fill=(255,0,0,255))
        icons,parts,labels=source_icons(source,2,1)
        result=recovered_icon(source,icons[0],parts,labels)
        self.assertEqual(result.size,(192,192))
        pixels=list(zip(*[iter(result.tobytes())]*4));visible=[pixel for pixel in pixels if pixel[3]>200]
        self.assertTrue(visible)
        self.assertTrue(all(pixel[:3]==(255,255,255) for pixel in visible))
        l,t,r,b=result.getbbox();self.assertGreater(l,0);self.assertLess(r,192)
        self.assertAlmostEqual((r-l)/(b-t),151/121,delta=.04)

    def test_ambiguous_joined_objects_are_rejected_before_import(self):
        source=Image.new('RGBA',(320,180));ImageDraw.Draw(source).rectangle((10,10,310,170),fill='white')
        with self.assertRaisesRegex(ValueError,'Inspect'):source_icons(source,2,1)
