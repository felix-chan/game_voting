import os

# List out all images
original = os.listdir('./original')


# Rename
i = 1
for images in original:
    new_file_name = './original/group{:02d}.jpg'.format(i)
    os.rename('./original/{}'.format(images), new_file_name)

    i += 1