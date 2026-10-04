import unittest
from PIL import Image,ImageDraw
from tools.install_construction_wall_kit import remove_neighbor_slivers,fit_axis


class WallKitExtractionTests(unittest.TestCase):
    def test_neighbor_fragment_is_removed_without_trimming_main_silhouette(self):
        image=Image.new('RGBA',(80,80));draw=ImageDraw.Draw(image)
        draw.rectangle((30,8,44,72),fill=(150,130,100,255))
        draw.rectangle((0,42,1,48),fill=(150,130,100,255))
        before=image.tobytes();clean,removed=remove_neighbor_slivers(image)
        self.assertTrue(removed);self.assertEqual(clean.getpixel((0,44))[3],0)
        self.assertEqual(clean.getchannel('A').getbbox(),(30,8,45,73))
        self.assertEqual(image.tobytes(),before)

    def test_legitimate_contiguous_piece_touching_edge_is_preserved(self):
        image=Image.new('RGBA',(80,80));ImageDraw.Draw(image).rectangle((0,30,70,44),fill=(90,100,110,255))
        clean,removed=remove_neighbor_slivers(image)
        self.assertEqual(removed,[]);self.assertEqual(clean.tobytes(),image.tobytes())

    def test_fitting_middle_preserves_authored_end_colors(self):
        image=Image.new('RGBA',(100,10),(100,100,100,255));draw=ImageDraw.Draw(image)
        draw.rectangle((0,0,19,9),fill=(255,0,0,255));draw.rectangle((80,0,99,9),fill=(0,0,255,255))
        result=fit_axis(image,140,True,20,20)
        self.assertEqual(result.size,(140,10));self.assertEqual(result.getpixel((5,5)),(255,0,0,255));self.assertEqual(result.getpixel((135,5)),(0,0,255,255))
