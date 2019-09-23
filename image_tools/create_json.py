import json

total_groups = 5
base_dir = '/files/upload_images/'

img_list = []

for i in range(total_groups):
    group_id = i+1
    img_list.append({

        'name': 'Group {}'.format(group_id),
        'full': '{dir}original/group{id:02d}.jpg'.format(
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

json_object = {
    'total_gp': total_groups,
    'images': img_list
}

with open('../images/files/json/images.json', 'w') as file:
    file.write(json.dumps(json_object))