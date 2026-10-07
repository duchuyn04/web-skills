# Photo library

106 photos for nail salon sites, in five groups: `interior` (19), `polish` (11), `tools` (23), `nails` (45), `pedicure` (8). Use them in salon.json as `"image": "lib:<id>"`; `python scripts/build.py --photos [group]` lists them.

Source: Openverse search of Flickr and other open collections, October 2026, licences CC BY 2.0, CC0 and Public Domain Mark only. `photos.json` keeps the title, creator, licence and original link of every photo; the build puts every library photo a site uses on `nguon-anh.html` (CC BY requires the credit).

Each photo was checked by eye. Left out: watermarks and text on the picture, readable polish brand labels and barcodes, shop names on signs or walls, faces and children, sports logos and licensed characters. Resized to 1280 px, JPEG quality 80.

Rules (enforced by the build):

- Library photos may illustrate the hero, service categories and the story. They are not the salon's work: on a real salon (`"demo": false`) the gallery takes only the owner's photos or drawn looks.
- No library photo for a technician.
- When the owner sends photos, they replace library photos.

Adding photos: same licences, same checks, then add an entry to `photos.json` with every field filled.
