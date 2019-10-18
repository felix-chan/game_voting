import json
import sys

total_groups = 16
if len(sys.argv) > 1:
    total_groups = int(sys.argv[1])

base_dir = '/files/upload_images/'

if total_groups > 1:
    print('There are {} groups in total'.format(
        total_groups
    ))
    
    img_list = []

    for i in range(total_groups):
        group_id = i+1
        img_list.append({

            'name': 'Table {}'.format(group_id),
            'full': '{dir}large/group{id:02d}.jpg'.format(
                dir=base_dir,
                id=group_id
            ),
            'small': '{dir}small/group{id:02d}.jpg'.format(
                dir=base_dir,
                id=group_id
            ),
            'large': '{dir}large/group{id:02d}.jpg'.format(
                dir=base_dir,
                id=group_id
            ),
        })
else:
    img_list = [{
        'name': 'QR code',
        'full': '{dir}/qr_code.png'.format(
            dir=base_dir
        ),
        'small': '{dir}/qr_code.png'.format(
            dir=base_dir
        ),
        'large': '{dir}/qr_code.png'.format(
            dir=base_dir
        )
    }]

json_object = {
    'total_gp': total_groups,
    'images': img_list
}

with open('../service/files/json/images.json', 'w') as file:
    file.write(json.dumps(json_object))