"""Build finite blood and spell effects with the existing portable Effekseer editor."""
from pathlib import Path
from copy import deepcopy
import math
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def set_value(parent,path,value):
    current=parent
    for key in path.split("/"):
        child=current.find(key)
        if child is None:child=ET.SubElement(current,key)
        current=child
    current.text=str(value)

def build():
    source=ROOT/"docs/art/effekseer/campfire.efkproj"
    editor=ROOT/"staging-ui/effekseer-fire-trial/editor/Tool/Effekseer.exe"
    if not editor.exists():raise FileNotFoundError("Run tools/build_effekseer_campfire.py to install the portable editor first")
    destination=ROOT/"frontend/public/assets/effekseer/combat-v1"
    (destination/"Texture").mkdir(parents=True,exist_ok=True)
    for name,life,count,color in [("blood",28,18,(255,255,255,220)),("spell",22,8,(255,255,255,240))]:
        image=Image.new("RGBA",(64,64))
        for y in range(64):
            for x in range(64):
                radius=math.sqrt(((x-31.5)/28)**2+((y-31.5)/(22 if name=="blood" else 28))**2)
                alpha=max(0,1-radius)**(.35 if name=="blood" else 1.6)
                image.putpixel((x,y),(255,255,255,round(alpha*255)))
        image.save(destination/"Texture"/f"{name}.png")
        tree=ET.parse(source);root=tree.getroot();children=root.find("Root/Children");node=deepcopy(children[0]);children.clear();children.append(node)
        set_value(root,"Root/Name",f"Fortcamp {name}");set_value(root,"EndFrame",60)
        set_value(node,"Name",name)
        for path,value in [("CommonValues/MaxGeneration/Infinite","False"),("CommonValues/MaxGeneration/Value",count),
            ("CommonValues/Life/Center",life),("CommonValues/Life/Min",life-5),("CommonValues/Life/Max",life+5),
            ("CommonValues/GenerationTime/Center",.2),("CommonValues/GenerationTime/Min",.2),("CommonValues/GenerationTime/Max",.2),
            ("RendererCommonValues/ColorTexture",f"Texture/{name}.png"),("RendererCommonValues/AlphaBlend",0 if name=="blood" else 1),
            ("RendererCommonValues/UV",0),
            ("RendererCommonValues/FadeIn/Frame",1),("RendererCommonValues/FadeOut/Frame",12)]:set_value(node,path,value)
        for axis in ("X","Y"):
            speed=.035 if name=="blood" else .018
            for key,value in [("Center",0),("Min",-speed),("Max",speed)]:set_value(node,f"LocationValues/PVA/Velocity/{axis}/{key}",value)
            for key in ("Center","Min","Max"):set_value(node,f"LocationValues/PVA/Location/{axis}/{key}",0)
            for key in ("Center","Min","Max"):
                set_value(node,f"ScalingValues/Easing/Start/{axis}/{key}",.09 if name=="blood" else .35)
                set_value(node,f"ScalingValues/Easing/End/{axis}/{key}",.035 if name=="blood" else .08)
        for component,value in zip(("R","G","B","A"),color):set_value(node,f"DrawingValues/Sprite/ColorAll_Fixed/{component}",value)
        for corner,(x,y) in {"LL":(-.5,-.5),"LR":(.5,-.5),"UL":(-.5,.5),"UR":(.5,.5)}.items():
            set_value(node,f"DrawingValues/Sprite/Position_Fixed_{corner}/X",x);set_value(node,f"DrawingValues/Sprite/Position_Fixed_{corner}/Y",y)
        project=ROOT/"docs/art/effekseer"/f"{name}.efkproj"
        ET.indent(tree);tree.write(project,encoding="utf-8",xml_declaration=True)
        # Relative textures resolved from the source project directory by the editor.
        (project.parent/"Texture").mkdir(exist_ok=True)
        import shutil
        shutil.copy2(destination/"Texture"/f"{name}.png",project.parent/"Texture"/f"{name}.png")
        subprocess.run([str(editor),"-cui","-in",str(project),"-e",str(destination/f"{name}.efk")],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        print(f"Built finite {name} effect")

if __name__=="__main__":build()
