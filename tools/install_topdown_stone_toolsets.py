"""Install additive overhead stone profiles; never replace existing material IDs."""
import json
from PIL import Image
from install_building_toolset import ROOT, groups, centered
from install_material_building_toolsets import PARTS

SOURCE = ROOT / 'staging-terrain/building-toolset-v5-topdown'
DEST = ROOT / 'frontend/public/assets/combat-terrain/structures/building-v5-topdown'


def mean(values):
    if not values:
        raise ValueError('Missing connecting masonry in candidate sprite')
    return sum(values) / len(values)


def main():
    registry_path = ROOT / 'frontend/src/map-prop-art.json'
    registry = json.loads(registry_path.read_text())
    geometry_path = ROOT / 'backend/building_art_geometry.json'
    geometry = json.loads(geometry_path.read_text())
    DEST.mkdir(parents=True, exist_ok=True)
    report = []
    for source_family in ('limestone', 'fieldstone'):
        family = source_family + '_plan'
        cells = groups(Image.open(SOURCE / (source_family + '.png')).convert('RGBA'), 4, 4)
        scale = 320 / cells[0][0].width
        sprites = {part: centered(cut, min(scale, 350 / max(cut.size)))
                   for part, (cut, _) in zip(PARTS, cells)}
        for prefix in ('door', 'gate'):
            pair = [cells[PARTS.index(prefix + '_' + state)][0] for state in ('closed', 'open')]
            anchors = []
            for cut in pair:
                alpha = cut.getchannel('A')
                # Measure the jambs, excluding the open leaf below their hinge.
                xs = list(range(max(1, cut.width // 7))) + list(range(cut.width * 6 // 7, cut.width))
                rows = [y for y in range(cut.height)
                        if sum(alpha.getpixel((x, y)) > 100 for x in xs) > len(xs) * .55]
                anchors.append(mean(rows))
            pair_scale = min(320 / max(c.width for c in pair),
                             175 / max(max(a, c.height - a) for c, a in zip(pair, anchors)))
            for state, cut, anchor in zip(('closed', 'open'), pair, anchors):
                sprites[prefix + '_' + state] = centered(cut, pair_scale, anchor)
        alpha = sprites['corner'].getchannel('A')
        cy = mean([y for x in range(40, 115) for y in range(192) if alpha.getpixel((x, y)) > 100])
        cx = mean([x for y in range(260, 335) for x in range(192, 384) if alpha.getpixel((x, y)) > 100])
        offset = round(((cx - 192) + (192 - cy)) / 384 * 1.25 / 2, 4)
        bounds = sprites['wall'].getchannel('A').getbbox()
        profile = {'plan_view': True, 'join_offset': offset,
                   'wall_half_thickness': round((bounds[3] - bounds[1]) / 384 * 1.25 / 2, 4),
                   'corner_offset': [round(offset - (cx / 384 - .5) * 1.25, 4),
                                     round(-offset - (cy / 384 - .5) * 1.25, 4)]}
        broken = sprites['corner_broken'].getchannel('A')
        by = mean([y for x in range(40, 110) for y in range(192) if broken.getpixel((x, y)) > 100])
        bx = mean([x for y in range(260, 335) for x in range(192, 384) if broken.getpixel((x, y)) > 100])
        profile['broken_corner_offset'] = [round(offset - (bx / 384 - .5) * 1.25, 4),
                                           round(-offset - (by / 384 - .5) * 1.25, 4)]
        breach = sprites['breach'].getchannel('A')
        rows = [y for x in list(range(40, 95)) + list(range(290, 340)) for y in range(384)
                if breach.getpixel((x, y)) > 100]
        profile['breach_offset'] = [0, round((.5 - mean(rows) / 384) * 1.25, 4)]
        end = sprites['end'].getchannel('A').getbbox()
        profile['end_offset'] = [round(.5 - (end[2] / 384 - .5) * 1.25, 4), 0]
        # Perimeter Ts are assembled from the straight band at the calibrated boundary.
        profile['junction_offset'] = [0, 0]
        geometry[family] = profile
        for part, sprite in sprites.items():
            filename = family + '_' + part + '.png'
            sprite.save(DEST / filename, optimize=True)
            registry['structure:' + family + '_' + part] = 'structures/building-v5-topdown/' + filename
            report.append({'family': family, 'part': part, 'source_box': list(cells[PARTS.index(part)][1])})
    registry_path.write_text(json.dumps(registry, indent=2) + '\n')
    geometry_path.write_text(json.dumps(geometry, indent=2) + '\n')
    (ROOT / 'frontend/src/building-art-geometry.json').write_text(json.dumps(geometry, indent=2) + '\n')
    (SOURCE / 'installed.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Added 32 overhead stone parts; existing material registrations and profiles preserved.')


if __name__ == '__main__':
    main()
