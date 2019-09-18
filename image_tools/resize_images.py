import os
from PIL import Image

# List out all images
original = os.listdir('./original')

# Create new directory
if not os.path.isdir('./small'):
    os.mkdir('small')
if not os.path.isdir('./large'):
    os.mkdir('large')

# Resize the images
for images in original:
    print("Resize image {}".format(images))
    img = Image.open('./original/{}'.format(images))
    bigsize = 1600
    smallsize = 1024

    wpercent_small = (smallsize/float(img.size[0]))
    if wpercent_small < 1:
        hsize_small = int((float(img.size[1])*float(wpercent_small)))
        img_small = img.resize((smallsize,hsize_small), Image.ANTIALIAS)
        img_small.save('./small/{}'.format(images))
    else:
        img.save('./small/{}'.format(images))

    wpercent_big = (bigsize/float(img.size[0]))
    if wpercent_big < 1:
        hsize_big = int((float(img.size[1])*float(wpercent_big)))
        img_big = img.resize((bigsize,hsize_big), Image.ANTIALIAS)
        img_big.save('./large/{}'.format(images))
    else:
        img.save('./large/{}'.format(images)) 