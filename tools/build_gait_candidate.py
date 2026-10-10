"""Reassemble existing/approved pose strips for the native Codex clock.

This is deterministic atlas assembly, not new artwork generation. Outputs stay
in staging until full gait QA approves both locomotion rows.
"""
from pathlib import Path
from hashlib import sha256
import argparse, json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SIZE = (1536, 2288)
CELL = (192, 208)
COUNTS = [7, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8]
MOVE_DURATIONS = [120] * 7 + [220]


def visible_rgba(image):
    pixels = np.array(image.convert('RGBA'))
    pixels[pixels[:, :, 3] == 0, :3] = 0
    return pixels


def assemble(source, gait_dir=None):
    atlas = source.copy()
    provenance = {}
    for row, state in [(1, 'running-right'), (2, 'running-left')]:
        if gait_dir:
            path = gait_dir / f'{state}.png'
            with Image.open(path) as strip:
                if strip.size != (1536, 208) or getattr(strip, 'n_frames', 1) != 1:
                    raise ValueError(f'{path}: require one static 8-cell 1536x208 strip')
                if 'A' not in strip.getbands():
                    raise ValueError(f'{path}: explicit alpha channel required')
                atlas.paste(strip.convert('RGBA'), (0, row * 208))
            provenance[state] = {'path': str(path), 'sha256': sha256(path.read_bytes()).hexdigest()}
        else:
            provenance[state] = {'path': 'assets/source-spritesheet.webp',
                                 'gaitStatus': 'incomplete opposite leading-foot half-cycle; assembly candidate only'}
    return Image.fromarray(visible_rgba(atlas)), provenance


def verify(atlas, source):
    if atlas.size != SIZE or getattr(atlas, 'n_frames', 1) != 1:
        raise ValueError('Native-clock candidate must be a static v2 atlas')
    a = visible_rgba(atlas)
    old = visible_rgba(source)
    motion = {}
    for row, count in enumerate(COUNTS):
        for col in range(count):
            cell = a[row*208:(row+1)*208, col*192:(col+1)*192]
            if not cell[:, :, 3].any():
                raise ValueError(f'Empty used cell {row},{col}')
        if a[row*208:(row+1)*208, count*192:, 3].any():
            raise ValueError(f'Unused cells must be transparent in row {row}')
        if row not in (1, 2) and not np.array_equal(a[row*208:(row+1)*208], old[row*208:(row+1)*208]):
            raise ValueError(f'Unrelated row {row} changed')
    for row, state in [(1, 'running-right'), (2, 'running-left')]:
        cells = [a[row*208:(row+1)*208, c*192:(c+1)*192] for c in range(8)]
        unique = len({sha256(c.tobytes()).hexdigest() for c in cells})
        if unique < 2:
            raise ValueError(f'{state}: duplicated columns bypass the host animation clock')
        motion[state] = {'distinctCells': unique, 'durationsMs': MOVE_DURATIONS,
                         'loopMs': sum(MOVE_DURATIONS),
                         'gaitVisualQA': 'required; distinct pixels do not prove foot alternation'}
    return {'ok': True, 'scope': 'file format, clock architecture and preserved artwork only',
            'size': list(SIZE), 'cell': list(CELL), 'spriteVersionNumber': 2,
            'imageFrames': 1, 'imageHasIndependentAnimationClock': False,
            'nonLocomotionRowsVisibleRGBAUnchangedFromReferenceBase': True, 'unusedCellsTransparent': True,
            'motion': motion}


def previews(atlas, outdir):
    contact = Image.new('RGB', (1536, 470), '#ecf6f3')
    draw = ImageDraw.Draw(contact)
    for row, state in [(1, 'running-right'), (2, 'running-left')]:
        cells = [atlas.crop((c*192, row*208, (c+1)*192, (row+1)*208)) for c in range(8)]
        animation = []
        y = (row-1)*235
        for col, cell in enumerate(cells):
            draw.text((col*192+5, y+3), f'{state} {col} / {MOVE_DURATIONS[col]}ms', fill='#284d56')
            contact.paste(cell, (col*192, y+25), cell)
            bg = Image.new('RGBA', CELL, '#ecf6f3')
            bg.alpha_composite(cell)
            animation.append(bg.convert('RGB'))
        animation[0].save(outdir/f'{state}.gif', save_all=True, append_images=animation[1:],
                          duration=MOVE_DURATIONS, loop=0)
    contact.save(outdir/'contact-sheet.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gait-dir', type=Path, help='Approved coherent right/left row strips; does not imply visual QA passed')
    parser.add_argument('--outdir', type=Path, default=ROOT/'work/gait-repair')
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    with Image.open(ROOT/'assets/source-spritesheet.webp') as original:
        source = original.convert('RGBA')
    if source.size != SIZE:
        raise ValueError('Source must be a v2 atlas')
    atlas, provenance = assemble(source, args.gait_dir)
    output = args.outdir/'candidate-spritesheet.webp'
    atlas.save(output, lossless=True, exact=True)
    with Image.open(output) as decoded:
        report = verify(decoded, source)
        if not np.array_equal(visible_rgba(decoded), visible_rgba(atlas)):
            raise ValueError('Encoding changed visible pixels')
    report.update({'atlasSha256': sha256(output.read_bytes()).hexdigest(), 'bytes': output.stat().st_size,
                   'provenance': provenance, 'locomotionArtworkUnchangedFromOriginalSource': args.gait_dir is None,
                   'releaseReady': False,
                   'releaseBlocker': 'complete alternating gait and independent visual QA required',
                   'actualCodexWindowVerified': False})
    (args.outdir/'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    previews(atlas, args.outdir)
    print(json.dumps({'output': str(output), 'bytes': report['bytes'], 'fileValidation': True,
                      'releaseReady': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
