"""
Generate list of QR code for each groups
"""

import hashlib
import qrcode
import json

total_groups = 16
group_list = {}

for i in range(16):
    # Generate hash key
    group_id = i + 1
    print('Working on Group {:02d}'.format(group_id))
    group_hash = 'SNP Table {:02d}'.format(group_id)
    md5_obj = hashlib.md5()
    md5_obj.update(group_hash.encode('utf-8'))
    md5_key = md5_obj.hexdigest()[0:10].upper()
    group_list[md5_key] = 'group{:02d}.jpg'.format(group_id)

    # Generate QR code
    url = 'http://felix.swiftzer.net/submit_gpimg/{key}/'.format(
        key=md5_key
    )
    img = qrcode.make(url)
    img.save("./qr_codes/group{:02d}.jpg".format(group_id))

# Save json file
with open('./qr_codes/all_codes.json', 'w') as file:
    file.write(json.dumps(group_list))