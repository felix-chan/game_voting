import os, re

# List out all images
original = os.listdir('./original')
original.sort()

# Rename
i = 1
for images in original:
    if re.search('\\.jpg', images.lower()):
        new_file_name = './original/group{:02d}.jpg'.format(i)
        print('Renaming {x1} to {x2}'.format(
            x1=images,
            x2=new_file_name
            ))
        os.rename('./original/{}'.format(images), new_file_name)

        i += 1